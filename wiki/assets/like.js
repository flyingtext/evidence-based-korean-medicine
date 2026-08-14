// 근거기반 한의학 위키 — 추천(좋아요) 버튼
// 정적 MkDocs 페이지에 추천 버튼을 주입하고 백엔드 API로 집계한다.
(function () {
  var API = window.LIKE_API || "http://localhost:8000";
  var STORAGE_KEY = "wiki_liked";

  function getPath() {
    // MkDocs가 생성한 페이지 경로 (index.html 제거)
    var p = window.location.pathname;
    if (p.endsWith("/")) p += "index.html";
    if (p.endsWith("index.html")) p = p.slice(0, -"index.html".length);
    return p || "/";
  }

  function getLiked() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function setLiked(arr) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(arr));
    } catch (e) {}
  }

  function fetchCount(path, cb) {
    fetch(API + "/api/likes")
      .then(function (r) { return r.json(); })
      .then(function (list) {
        for (var i = 0; i < list.length; i++) {
          if (list[i].path === path) { cb(list[i].count); return; }
        }
        cb(0);
      })
      .catch(function () { cb(null); });
  }

  function render() {
    var content = document.querySelector(".md-content__inner");
    if (!content) return;
    var path = getPath();
    var liked = getLiked().indexOf(path) !== -1;

    var wrap = document.createElement("div");
    wrap.className = "wiki-like";
    wrap.style.cssText =
      "margin:0 0 1.2rem;padding:.6rem 1rem;border:1px solid var(--md-default-fg-color--light);" +
      "border-radius:.4rem;display:flex;align-items:center;gap:.6rem;font-size:.9rem;";

    var btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = liked ? "추천됨" : "추천";
    btn.style.cssText =
      "cursor:pointer;padding:.35rem .8rem;border-radius:.3rem;border:1px solid var(--md-primary-fg-color);" +
      "background:" + (liked ? "var(--md-primary-fg-color)" : "transparent") + ";" +
      "color:" + (liked ? "#fff" : "var(--md-primary-fg-color)") + ";";

    var label = document.createElement("span");
    label.textContent = "추천 0";

    function setCount(n) {
      label.textContent = "추천 " + (n == null ? "-" : n);
    }

    btn.addEventListener("click", function () {
      if (liked) return;
      fetch(API + "/api/like", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: path }),
      })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          liked = true;
          btn.textContent = "추천됨";
          btn.style.background = "var(--md-primary-fg-color)";
          btn.style.color = "#fff";
          setCount(d.count);
          var arr = getLiked();
          arr.push(path);
          setLiked(arr);
        })
        .catch(function () { setCount(null); });
    });

    wrap.appendChild(btn);
    wrap.appendChild(label);
    content.insertBefore(wrap, content.firstChild);

    fetchCount(path, setCount);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", render);
  } else {
    render();
  }
})();
