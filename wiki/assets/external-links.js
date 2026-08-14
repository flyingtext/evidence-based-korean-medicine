(function () {
  function handle() {
    var origin = location.origin;
    document.querySelectorAll("a[href]").forEach(function (a) {
      var href = a.getAttribute("href") || "";
      var isExternal =
        (href.indexOf("://") !== -1 || href.indexOf("//") === 0) &&
        href.indexOf(origin) !== 0;
      if (isExternal) {
        a.setAttribute("target", "_blank");
        a.setAttribute("rel", "noopener noreferrer");
      }
    });
  }
  document.addEventListener("DOMContentLoaded", handle);
  document.addEventListener("DOMContentSwitch", handle);
})();
