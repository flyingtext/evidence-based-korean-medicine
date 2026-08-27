# X-ray 검사(단순 방사선 검사, Plain Radiography)

X-ray 검사(단순 방사선 검사, X線 檢査, Plain Radiography)는 X선(X-ray)을 인체에 투과시켜 조직별 감약(減弱, attenuation) 차이를 2차원 영상으로 재구성하는, 근골격계 영상진단의 1차 검사(first-line imaging)이다. 한의사 임상가에게 단순 방사선 검사는 (1) 침구·추나·약침 등 한방 시술 전 골절·탈구·감염·종양 같은 시행 금기를 배제하는 안전판(safety gate), (2) 척추측만증·척추관협착증·퇴행성관절염 등 만성 근골격계 질환의 중증도를 객관적으로 계층화하는 도구, (3) 치료 반응·경과를 추적하는 참고자료라는 세 가지 역할을 동시에 수행한다. 본 문서는 X선의 물리적 원리부터 표준 촬영 자세, 판독의 기초 체계, 근골격계 질환군별 활용, 방사선 안전성, 그리고 초음파·CT·MRI와의 비교·선택 기준까지를 독립된 방법론 표제어로 다룬다. 개별 질환의 세부 병인병기·변증·치료(침구·본초·추나)는 각 질환 문서(요통·경추통·척추관협착증·골관절염·골다공증성척추압박골절 등)에서 다루며, 본 문서는 그 질환 문서들이 공통으로 전제하는 **영상 촬영·판독 방법론** 자체에 집중한다. `영상 진단 필수 근골격계 질환` 문서가 "언제 영상검사를 의뢰해야 하는가"라는 임상결정(clinical decision) 관점을 다룬다면, 본 문서는 "X-ray가 어떻게 촬영되고 어떻게 읽히는가"라는 촬영·판독 기법 자체를 다루어 서로 보완적이다.

---

## 제1편 정의·원리·역사

### 1-1. X선의 물리적 원리

X선은 파장 약 0.01~10 nm의 전자기파로, X선관(X-ray tube)의 음극에서 방출된 전자가 고전압으로 가속되어 양극(주로 텅스텐)에 충돌할 때 제동복사(bremsstrahlung)와 특성 X선(characteristic X-ray)의 형태로 발생한다[교과서적 근거]. X선이 인체를 통과할 때 조직의 밀도와 원자번호에 비례해 광전효과(photoelectric effect)와 콤프턴 산란(Compton scattering)에 의한 감약이 일어나며, 뼈(칼슘·인 함량이 높아 감약이 큼)는 영상에서 밝게(방사선 비투과성, radiopaque), 공기를 포함한 폐·연부조직은 상대적으로 어둡게(방사선 투과성, radiolucent) 나타난다[교과서적 근거]. 진단영상의학 교과서는 X선관·검출기(필름-스크린 또는 디지털 평판검출기, flat-panel detector)·시준기(collimator)·그리드(grid) 등 장비 구성요소별 물리적 특성과 환자 선량에 미치는 영향을 정리하고 있으며, 관전압(kVp)·관전류(mAs)·초점-필름 거리(FFD) 조절이 대조도(contrast)·해상도·피폭선량을 동시에 결정하는 요인임을 강조한다[^92]. 진단영상의학의 환자 선량학(patient dosimetry) 문헌은 각 촬영 부위별 실효선량(effective dose)이 촬영 기법·장비 세대·환자 체형에 따라 수배까지 차이 날 수 있음을 정리했다[^91].

### 1-2. 근골격계 영상진단에서 단순 방사선 검사의 위치

단순 방사선 검사는 CT·MRI·초음파에 비해 공간 해상도가 우수하고 검사 시간이 짧으며 비용이 낮아, 골절·탈구·퇴행성 변화·정렬 이상(alignment) 평가의 1차 검사로 자리매김해 왔다[교과서적 근거]. 미국영상의학회(ACR)의 적정성 기준(Appropriateness Criteria)은 늑골 골절이 의심되는 흉부 외상에서도 단순촬영을 초기 평가의 근간으로 권고하면서, 임상 소견에 따라 CT로 단계적으로 확대하는 알고리즘을 제시한다[^10]. 골·연부조직 종양이 의심되는 경우에도 단순촬영에서의 골 파괴 양상·골막 반응·기질(matrix) 석회화 패턴이 감별진단의 출발점이 된다[^94].

### 1-3. 역사적 발전 — 필름-스크린에서 디지털 방사선촬영으로

전통적 필름-스크린 방사선촬영은 1990년대 이후 컴퓨터 방사선촬영(computed radiography, CR)과 디지털 방사선촬영(digital radiography, DR)으로 전환되었다. 일본에서 시행된 초기 CR(Fuji computed radiography, FCR) 임상 평가는 비전문의도 포함한 판독자 사이에서 기존 필름 대비 진단능이 유지되거나 향상됨을 보고했다[^70]. 이후 디지털 검출기의 개선은 회백조정(gray-scale adaptation) 자동화[^114], 골 억제(bone suppression) 후처리 영상을 통한 미세 병변 검출력 향상[^76] 등으로 이어졌으며, 최근에는 흉부 단순촬영에서 골 소견(예: 척추 압박변형)을 별도로 추출하는 딥러닝 후처리 기법까지 개발되고 있다[^114][^117]. 이 근거 한계 명시: 위 역사적 개발 근거는 대부분 개별 기관·모델 단위의 기술 검증 연구로, 국내 임상 현장 전반의 표준으로 일반화하기에는 추가 다기관 검증이 필요하다.

---

## 제2편 촬영 기법·표준 자세

### 2-1. 촬영 기법의 기본 원칙

표준 촬영은 부위별로 전후방(AP, anteroposterior) 또는 후전방(PA, posteroanterior), 측면(lateral), 사위(oblique) 등 최소 2방향 이상을 원칙으로 하여 입체 구조를 2차원 평면 두 장 이상으로 재구성한다[교과서적 근거]. 흉부 방사선촬영에서는 관전압을 높이고(고kVp 기법) 구리 필터를 추가해 골 구조에 의한 대조도를 낮추고 폐야의 대조도를 상대적으로 높이는 기법이 사용되며, 이러한 관전압·필터 조합에 대한 최적화는 검출기 세대에 따라 최적 조건이 달라진다는 것이 진단영상 판독체계 연구들에서 공통적으로 지적된다[^75]. 척추 방사선촬영에서는 서있는 자세(standing/weight-bearing)로 촬영해야 체중 부하 상태에서의 정렬(alignment)을 반영할 수 있다는 원칙이 척추정렬 지표 연구들에서 공통적으로 전제된다[^54][^24].

### 2-2. 부위별 표준 촬영 자세

| 부위 | 표준 촬영 | 임상적 의미 | 근거 |
| --- | --- | --- | --- |
| 흉부 | 후전방(PA) + 측면(lateral), 필요 시 좌측면(left lateral) | 심장·종격동·폐야 평가, 심흉비(cardiothoracic ratio) 산출 | 휴대용 전후방(AP portable) 촬영에서의 심흉비 계산법이 표준 후전방 촬영과 체계적으로 다름을 보정한 연구 [^119] |
| 늑골 | 전용 늑골 촬영(rib series) + 흉부 PA | 단순 늑골통에는 과잉촬영 지양, 외상성 골절 의심 시 시행 | ACR 적정성 기준 [^10] |
| 요추 | 전후방(AP) + 측면(lateral), 필요 시 굴곡-신전(flexion-extension) 측면 | 척추전방전위증·불안정성 평가 | 척추정렬 지표(요추 전만각 등)의 표준 측정법 연구 [^54] |
| 경추 | 전후방(AP) + 측면(lateral) + 치돌기(open-mouth odontoid) | 상부경추 골절·아탈구·전만 평가 | 경추 시상면 정렬 파라미터의 딥러닝 자동측정 연구 [^12] |
| 골반·고관절 | 전후방(AP) 골반 + 개구리다리(frog-leg lateral) | 대퇴골두·비구 형태, 관상면 정렬 평가 | 관상면 정렬 파라미터(CPAK 분류) 연구 [^28][^25] |
| 슬관절 | 체중부하 전후방(weight-bearing AP) + 측면 + 슬개골축상(sunrise/skyline view) | Kellgren-Lawrence 등급 판정의 표준 자세 | K-L 체계 표준화 연구 [^17] |
| 발목 | 전후방(AP) + 측면 + 격자상(mortise view) | 골절선·격자 간격 평가 | Ottawa Ankle Rule 검증 연구 [^60] |
| 전신 척추(scoliosis series) | 서있는 자세 전신 후전방(standing PA) + 측면 | Cobb각 측정, 성장기 추적관찰 | Cobb각 측정 신뢰도 연구 [^36] |
| 손목 | 후전방(PA) + 측면 + 사위(oblique) | 미세 골절 검출 | 딥러닝 보조 손목 골절 진단 연구 [^112] |

이 표는 임상 틀이지 동일 근거수준의 권고가 아니다. 실제 촬영 프로토콜은 기관별 장비·환자 상태에 따라 조정되며, 표준 자세를 확보하기 어려운 응급 상황(휴대용 촬영 등)에서는 판독 시 자세 보정을 고려해야 한다.

### 2-3. 척추·관절 촬영의 원칙 — 체중부하와 재현성

척추측만증 추적관찰에서는 매 촬영마다 동일한 자세(서있는 자세, 발 위치 고정)를 재현하는 것이 Cobb각 측정의 신뢰도를 좌우한다[^36]. 슬관절·고관절의 정렬 평가에서도 체중부하 여부가 관절 간격(joint space width) 측정치에 영향을 주므로, 비체중부하 촬영에서 관절 간격이 과대평가될 수 있다는 점이 관상면 정렬 연구들에서 일관되게 지적된다[^27][^26]. 요추 골반 정렬 지표(골반경사각 pelvic incidence·요추전만각 lumbar lordosis)는 반드시 서있는 자세에서 측정해야 임상적으로 의미 있는 수치가 되며, 고관절 골관절염 환자에서 골반경사각·요추전만각·요추 유연성 간의 상관관계를 분석한 연구는 이 원칙을 임상적으로 뒷받침한다[^54].

### 2-4. 촬영 관련 신기술 — 인공지능 보조 판독·측정

최근에는 인공지능(AI)이 표준 촬영 영상에서 해부학적 지표를 자동 측정하는 기술이 빠르게 발전했다. 요추-천골 이행부의 해부학적 파라미터를 자동 측정하는 X-ray 기반 AI 측정 기술[^109], 이면상(biplanar) X-ray로부터 요추 3차원 재구성을 수행하는 다중과제 딥러닝 모델[^108], 다시점(dual-view) X-ray로 척추측만증을 평가하는 투영 모델[^101], 척추 정렬을 다기관 규모로 평가하는 확장 가능한 AI 시스템[^100] 등이 보고되었다. 이러한 기술은 촬영 이후 판독 단계의 재현성·효율성을 높이는 보조 도구로 위치하며, 촬영 기법 자체(자세·노출 조건)의 표준화를 대체하지 못한다는 점에 유의해야 한다.

---

## 제3편 판독 기초

### 3-1. 체계적 판독 접근법(ABCS 원칙)

근골격계 단순 방사선의 체계적 판독은 흔히 A(Alignment, 정렬)-B(Bone density, 골밀도)-C(Cartilage space, 연골간격/관절간격)-S(Soft tissue, 연부조직)의 네 요소를 순서대로 확인하는 방식으로 요약된다[교과서적 근거]. 정렬 평가에서는 척추체·관절면의 나열이 정상 곡선(경추전만·흉추후만·요추전만)을 유지하는지, 척추전방전위증·아탈구가 있는지를 본다[교과서적 근거]. 골밀도 평가에서는 피질골(cortical bone)의 두께·투명도, 해면골(trabecular bone)의 골소주 양상을 관찰하며, 관절간격 평가에서는 좌우 대칭·간격 협소화 유무를, 연부조직 평가에서는 관절낭 팽창·연부조직 종창·이물질 유무를 확인한다[교과서적 근거].

### 3-2. 골절 판독의 기본 원칙

골절의 방사선학적 진단은 골 피질의 불연속선(cortical break), 골절선(fracture line), 골절편 전위(displacement)·성각(angulation)의 확인을 기본으로 한다[교과서적 근거]. 응급 상황에서 임상결정규칙(clinical decision rule)을 적용해 불필요한 촬영을 줄이는 접근이 표준화되어 있는데, 대표적으로 오타와발목규칙(Ottawa Ankle Rule)은 발목 외상 후 특정 부위 압통과 체중부하 보행 가능 여부만으로 골절 가능성을 선별하며, 원 연구는 민감도가 매우 높아(거의 모든 골절을 놓치지 않음) 촬영률을 유의하게 낮출 수 있음을 보고했다[^60]. 이 규칙을 중국 방어 환경(군진 의료)에 적용한 연구에서도 적용 가능성이 확인되었다[^61]. 소아·청소년에서 임상의가 시행하는 현장초음파(point-of-care ultrasound)가 골절 진단의 보조 수단이 될 수 있다는 관찰연구도 있으나, 최종 진단은 여전히 단순촬영을 기준으로 한다[^64].

### 3-3. 관절 간격·골밀도 소견 판독의 기초

관절간격 협소화는 연골 소실을 간접적으로 반영하는 대표 소견이며, Kellgren-Lawrence(K-L) 등급체계가 슬관절·고관절 골관절염의 방사선학적 중증도 판정 표준으로 가장 널리 쓰인다[^17]. K-L 체계와 OARSI 아틀라스 기준을 비교한 연구는 진단 기준에 따라 유병률 추정치가 달라질 수 있음을 보여, 판독 기준의 일관된 적용이 중요함을 시사한다[^17]. 골밀도의 정성적 판독(피질골 얇아짐, 투명도 증가)은 이중에너지 X-ray 흡수계측법(dual-energy X-ray absorptiometry, DXA)의 정량적 T-score와 상호 보완적으로 활용된다[^38][^39]. 척추체 압박골절의 반정량적(semiquantitative) 평가법은 척추체 높이 감소 정도(경도·중등도·고도)로 등급화하며, 숙련 판독자와 비숙련 판독자 간 일치도를 비교한 연구는 판독자 훈련의 중요성을 뒷받침한다[^81]. 이러한 반정량적 판독을 자동화하려는 시도로, 고령 여성의 흉부 측면 방사선에서 압박골절을 자동 검출하는 소프트웨어가 개발·검증되었다[^116].

### 3-4. 정상 변이와 위양성·위음성

단순 방사선은 연부조직 병변이나 초기 골수 침범을 놓칠 수 있어 위음성 가능성이 있으며, 실제로 CT는 방사선에서 보이지 않는 골다공증성 종판 함몰(endplate depression)을 방사선보다 더 많이 검출한다는 비교연구가 보고되었다[^73]. 반대로 성장판 잔유물, 부골(accessory ossicle), 영양공(nutrient foramen) 등 정상 변이를 병변으로 오인하는 위양성도 흔하며, 쇄골 내측 골단(medial clavicular epiphysis)의 골화 정도를 골연령 판정에 이용하는 연구는 정상 발달 변이 해석의 중요성을 보여준다[^77]. 판독자 훈련·경력에 따라 미세 병변 검출력에 차이가 있다는 점은 골 억제 영상 기법의 판독자 숙련도별 효과 연구에서도 확인된다[^76]. 짧은 표준화 훈련만으로도 특정 질환(진폐증 등)의 방사선 판독 정확도가 유의하게 향상될 수 있다는 임상시험은 판독 역량이 반복 훈련을 통해 개선될 수 있는 기술임을 뒷받침한다[^15].

### 3-5. 인공지능 보조 판독의 성능과 한계

최근 K-L 등급 판정을 포함한 다양한 근골격계 X-ray 판독에 딥러닝 기반 인공지능(AI)이 적용되고 있다. 딥러닝 기반 X-ray 기법이 슬관절 골관절염 K-L 등급을 검출·분류하는 성능을 종합한 체계적 고찰·메타분석은 우수한 진단 정확도를 보고했다[^6]. AI 기반 K-L 자동 등급 소프트웨어를 다기관 코호트에서 검증한 연구도 유사한 결론을 보였다[^35]. 슬관절 인공관절 수술 영역에서 AI 기반 X-ray 영상분석 적용을 종합한 체계적 고찰도 발표되었다[^4]. 그러나 이러한 AI 보조판독은 사람 판독자를 완전히 대체하기보다 판독 효율·재현성을 보조하는 도구로 자리매김하고 있으며, 류마티스내과 영역의 AI·딥러닝 개관 문헌 역시 임상 통합 시 검증·해석가능성(explainability)의 중요성을 강조한다[^89]. 골절위험 평가에 AI를 통합하는 흐름을 개관한 문헌도 임상 영상을 활용한 예측이라는 잠재력과 함께, 예측 불확실성에 대한 신중한 접근을 당부한다[^90]. 흉부영역에서는 AI 보조판독과 기존 판독을 비교한 실용적 무작위 임상시험이 응급실 급성 호흡기 증상 환자에서 진단 정확도·워크플로 효율성을 평가했다[^14]. 흉부방사선 판독에서 방사선사(radiographer)의 훈련이 판독 역량을 보완할 수 있다는 연구도 있다[^67]. 이 근거 한계 명시: AI 보조판독 근거는 대부분 특정 기관·특정 모델 단위의 검증 연구이며, 국내 한의 임상 현장에 그대로 일반화하기보다는 최종 판독은 영상의학과 전문의 소견을 기준으로 삼아야 한다.

**변증 층도 강조**: 한의사가 단순 방사선을 직접 판독하는 경우에도, 변증 없는 관행적 취혈/처방은 근거에 부합하지 않는다는 원칙은 영상 판독 이후의 치료 결정에도 동일하게 적용된다. 영상 소견은 진단의 한 축일 뿐, 반드시 변증·이학적 검사와 종합해 치료계획을 수립해야 한다.

---

## 제4편 근골격계 질환별 활용

이 편은 척추·관절·골절 등 질환군별로 X-ray의 판독 방법론(어떤 지표를 어떻게 측정·판독하는가)에 집중한다. 질환별 병인병기·변증·치료(침구·본초·추나)의 상세 서술은 각 질환 문서에서 다루며, 응급 의뢰 기준(레드플래그) 등 "언제 영상을 의뢰할 것인가"의 임상결정 흐름은 `영상 진단 필수 근골격계 질환` 문서를 따른다.

### 4-1. 척추 정렬·퇴행성 척추질환군 (KCD-8: M47, M48, M54)

①코드: M47(척추증), M48(척추관협착증 등), M54(기타 등병증). ②병인병기: 한의학적으로는 신허(腎虛)·간신부족(肝腎不足)으로 인한 골수 실양(失養), 어혈(瘀血)·기체(氣滯)로 인한 경락 조체가 척추 퇴행의 병기로 설명된다[교과서적 근거]. ③병태생리: 요추 방사선 소견에서 추간판 높이 감소, 골극(osteophyte) 형성, 척추전방전위증이 관찰되며, 전직 엘리트 운동선수 코호트 연구는 반복적 기계적 부하가 요추 방사선학적 변화의 위험요인임을 보고했다[^24]. 요추 척추증의 새로운 요소별 등급체계는 인구 기반 코호트에서 개발·검증되었다[^19]. 혈청 펜토시딘(pentosidine) 농도가 요추 척추증의 방사선학적 중증도와 연관된다는 관찰연구는 최종당화산물 축적과 척추 퇴행의 생물학적 연결을 시사한다[^20]. ④치료: 방사선 소견상 경도~중등도 퇴행성 변화는 침구·한약·추나 등 보존치료의 대상이 되며, 변증에 따른 치법 선택이 우선한다[교과서적 근거]. ⑤예후: 방사선학적 중증도와 통증·기능 정도가 항상 비례하지 않는다는 원칙은 슬관절 골관절염에서 확인된 영상-증상 불일치 현상과 마찬가지로 척추 퇴행성 변화에도 적용되므로[^31], 영상 소견만으로 예후를 단정하지 않는다. ⑥관리: 정기적 추적촬영 여부는 증상 변화·신경학적 소견에 따라 결정한다.

### 4-2. 골관절염군 (KCD-8: M15-M19)

①코드: M15(다발관절증), M16(고관절증), M17(무릎관절증), M19(기타 관절증). ②병인병기: 간주근(肝主筋)·신주골(腎主骨) 이론에 따라 간신부족·기혈허약이 관절 퇴행의 근본 병기로, 풍한습사(風寒濕邪) 침습이 유발인자로 설명된다[교과서적 근거]. ③병태생리: Kellgren-Lawrence 등급체계가 슬관절 골관절염 방사선학적 중증도 판정의 표준으로, K-L 체계와 OARSI 아틀라스 비교 연구는 두 기준 간 유병률 추정치 차이를 보고했다[^17]. 한국 국민건강영양조사 자료를 이용한 대규모 연구들은 50세 이상 한국 성인에서 방사선학적 슬관절 골관절염의 유병률과 인구학적 연관 요인[^34], 흡연량과의 연관성[^30], 대사증후군과 척추 골관절염의 연관성[^32]을 각각 보고했다. 중국의 3만여 명 규모 전국 조사도 방사선학적 슬관절 골관절염의 유병률을 보고했다[^22]. 진행성 방사선학적 슬관절 골관절염이 있음에도 통증이 없는 경우가 상당수 존재한다는 관찰은 영상 소견과 임상증상의 불일치를 뒷받침한다[^31]. 무릎 외에 수부 골관절염도 표준화된 방사선 판독 대상이며, 카신-벡병(Kashin-Beck Disease) 성인 코호트에서 수부 골관절염의 방사선학적 특징을 분석한 연구는 지역성 골관절병의 감별에 수부 X-ray가 유용함을 보여준다[^21]. K-L 등급이 높을수록 노쇠(frailty) 지표가 악화된다는 연관성도 보고되었다[^33]. 관상면 정렬(Coronal Plane Alignment of the Knee, CPAK) 분류를 이용한 최근 연구들은 K-L 등급 증가에 따라 구성적 내반(constitutional varus) 방향으로 정렬이 이동함을 보였고[^26][^28][^27][^29][^25], 발목 골관절염에서는 원위경비인대결합(distal tibiofibular syndesmosis) 형태 분류와의 연관성이 보고되었다[^23]. ④치료: 방사선 등급이 아닌 증상을 기준으로 침구·한약 치료를 시작하는 것이 근거에 부합하며, 경도의 K-L 등급에서도 근력강화·관절가동 운동이 병행될 때 증상 호전이 보고된 바 있다[^11]. ⑤예후: K-L 등급이 예후 예측에 참고가 되나 절대적이지 않다[^31][^33]. ⑥관리: 방사선 재촬영은 증상 악화, 수술적 치료 고려 시점에 시행한다.

**감별진단 표**: 골관절염과 감별해야 할 방사선학적으로 유사한 관절병증(류마티스관절염의 대칭적 미란·골감소, 통풍의 천공형 골결손, 화농성 관절염의 급성 관절간격 소실 등)은 임상 경과·혈액검사와 종합해 감별한다. 이 표는 임상 틀이지 동일 근거수준의 권고가 아니다.

### 4-3. 골다공증·척추압박골절군 (KCD-8: M80-M81, S32 등)

①코드: M80(병적골절 동반 골다공증), M81(병적골절 없는 골다공증), S32(요추·골반 골절). ②병인병기: 신허(腎虛)로 인한 골수 화생 부족이 골다공증의 핵심 병기로 설명된다[교과서적 근거]. ③병태생리: DXA 기반 골밀도 측정이 골다공증 진단의 정량적 표준이며, 한국인 대상 요추·고관절 골밀도 참조치[^49], 소아청소년 참조치[^50] 등 인구집단별 기준치 연구가 축적되어 있다. 척추체 압박골절의 반정량적 평가법에 대한 숙련도별 판독 일치도 연구[^81], 척추체 형태계측 평가(morphometric vertebral assessment)가 약물치료 대상자 선별에 중요하다는 연구[^84], 기존 척추골절이 향후 골절을 예측한다는 코호트 연구[^82] 등이 척추압박골절 판독의 임상적 가치를 뒷받침한다. 홍콩과 로마 코호트를 비교한 연구는 인종 간 골다공증성 척추골절 유병률·중증도 차이를 보고했으며[^79], 일본 ROAD 연구는 경도-중등도 골절의 연관요인이 서로 다름을 보고했다[^80]. 골밀도와 척추-대퇴부 T-score 불일치(discordance)의 빈도·위험요인도 보고되었다[^56]. T-score를 이용한 척추-고관절 불일치 개념은 척추손상 환자의 골다공증 유병률 추정에도 활용된다[^46]. DXA 기반 척추골절평가(VFA) 영상으로부터 산출한 "척추 나이"가 향후 골절·사망을 예측한다는 최근 연구도 있다[^52]. VFA의 진단 정확도를 종합한 체계적 고찰은 폐경 후 여성·고령 남성에서 VFA가 골절 위험 평가에 기여함을 정리했다[^5]. 정량적 컴퓨터단층촬영(QCT)과 DXA로 측정한 골밀도가 골다공증성 척추골절 위험을 얼마나 잘 예측하는지 비교한 메타분석은 두 정량 영상기법이 상호 보완적으로 위험도 평가에 기여할 수 있음을 보여준다[^7]. ④치료: 급성 압박골절 확진 전에는 복와위 강한 수기치료·척추 압박 시술을 피하고, 확진 후 안정화 단계에서 통증관리 목적 침구치료를 병행할 수 있다[교과서적 근거]. 골시멘트를 이용한 척추성형술의 안전성·유효성에 대한 전향적 예비연구도 참고할 수 있다[^16]. ⑤예후: 척추골 스캔(bone scan)이 압박골절의 급성기 판정에 실용적으로 활용될 수 있다는 연구가 있다[^85]. ⑥관리: DXA 재검 간격은 골절 위험도·치료 반응에 따라 조정하며, 임상 현장에서의 재검 간격 실태 연구도 참고할 수 있다[^39].

### 4-4. 척추측만증·소아청소년 척추변형군 (KCD-8: M41)

①코드: M41(척추측만증). ②병인병기: 성장기 근골격계의 기혈 불균형, 경근(經筋) 불균형이 측만 발생과 진행의 병기로 설명된다[교과서적 근거]. ③병태생리: 중국 아동 대상 체계적 고찰·모델링 연구는 연령·성별·지역·아형에 따른 유병률 변이를 정리했다[^1]. 청소년 특발성 척추측만증 선별·진단의 신기술 적용에 대한 범위 고찰(scoping review)도 발표되었다[^3]. Cobb각은 여전히 진단·추적관찰의 표준 지표이며, 초음파 기반 각도 측정법의 신뢰도·타당도를 검증한 연구는 방사선 촬영 대체·보완 수단으로서의 가능성을 뒷받침한다[^36]. 표면지형(surface topography)을 이용한 방사선 무노출 추적관찰의 역할을 정리한 문헌 고찰도 있다[^86]. ④치료: 방사선학적 진행 정도에 따라 관찰·보조기·수술 여부가 결정되며, 추나 등 한방 수기치료를 병행하는 경우에도 방사선 추적관찰 원칙은 유지한다[교과서적 근거]. ⑤예후: 반복 방사선 촬영에 따른 누적 피폭이 장기적 암·사망 위험과 연관될 수 있다는 체계적 고찰·메타분석은 촬영 빈도 관리의 중요성을 뒷받침한다[^8](상세는 제5편). ⑥관리: 성장기에는 초음파·표면지형 등 방사선 무노출 기법을 병행해 촬영 빈도를 줄이는 전략이 권장된다[^36][^86].

### 4-5. 경추·경부 질환군 (KCD-8: M47.0, M50, M54.2)

①코드: M47.0(척추동맥압박증후군), M50(경추간판장애), M54.2(경부통). ②병인병기: 항강(項強)·낙침(落枕) 등 경항부 기혈 조체가 병기로 설명된다[교과서적 근거]. ③병태생리: 경추 시상면·국소 정렬 파라미터를 딥러닝으로 자동 측정하는 기법이 개발되어 대규모 한국인 성인 코호트에서 경추 만곡의 시간적 추이를 분석하는 데 활용되었다[^12](자동측정 방법론은 관련 연구군 참조). 경추 디스크 치환술의 임상·방사선학적 결과를 비교한 임상시험도 척추 정렬 평가에서 방사선 지표를 핵심 결과변수로 사용한다[^12]. 퇴행성 경추 척수병증에서 새로운 영상 기법을 정리한 문헌 고찰은 단순촬영이 여전히 정렬·불안정성 선별의 출발점임을 강조한다[^88]. ④치료: 신경학적 결손이 없는 전형적 경부통은 방사선 없이 침구·추나 등 보존치료를 우선 시행할 수 있다[교과서적 근거]. ⑤예후: 경추 정렬 이상이 확인되면 추나 강도·방향 결정에 참고한다. ⑥관리: 외상력·신경학적 결손이 있으면 즉시 영상 의뢰 원칙(레드플래그)을 따른다.

### 4-6. 골절·외상성 손상군 (KCD-8: S 전 범위)

①코드: S02, S12, S22, S32, S42, S52, S62, S72, S82, S92(부위별 골절), T02(다발골절). ②병인병기: 외상으로 인한 어혈(瘀血)·기체(氣滯)가 통증의 병기로 설명되며, 정골(整骨) 후 활혈화어(活血化瘀) 치법이 적용된다[교과서적 근거]. ③병태생리: 임상결정규칙(Ottawa Ankle Rule 등)이 불필요한 촬영을 줄이면서도 골절을 놓치지 않는 선별 도구로 검증되었다[^60][^61]. 손목 골절 진단에서 딥러닝 기반 주의집중(attention) 메커니즘을 적용한 영상분석 모델의 진단 성능 향상 연구도 보고되었다[^112]. 발목·발 골절 진단에서 컬러 도플러 초음파의 역동적 스캐닝이 보조적으로 활용될 수 있다는 증례가 있다[^97]. ④치료: 골절이 확인되거나 강력히 의심되면 정복·고정이 우선이며, 한방 수기치료는 정복·고정 이후 재활 단계에서 협진 형태로 병행한다[교과서적 근거](상세는 `영상 진단 필수 근골격계 질환` 문서 참조). ⑤예후: 골절 유형·전위 정도가 예후와 직결된다. ⑥관리: 정복 전후 반드시 방사선으로 확인한다.

### 4-7. 천장관절·척추관절병증군 (KCD-8: M45, M46)

①코드: M45(강직척추염), M46(기타 척추병증, 천장관절염 포함). ②병인병기: 신허(腎虛)·독사(毒邪)의 침습이 병기로 설명된다[교과서적 근거]. ③병태생리: 장병성 관절병증(enteropathic arthritis)이 천장관절을 침범할 때의 영상 소견과 감별진단을 정리한 문헌은 천장관절 미란·경화·유합의 방사선학적 진행 단계를 체계적으로 제시한다[^62]. ④치료: 천장관절통이 확인되면 침구·약침과 함께 염증성 척추관절병증 감별(활동성 염증표지자·HLA-B27 등)이 선행되어야 한다[교과서적 근거]. ⑤예후: 만성 염증성 변화는 조기 개입이 강직 진행을 늦추는 데 중요하다[교과서적 근거]. ⑥관리: 추적 방사선 소견으로 강직·유합 진행 여부를 평가한다.

### 4-8. 질환군별 X-ray 추적 지표표

한방 치료(침구·한약·추나)의 경과를 X-ray로 추적할 때, 질환군마다 어떤 방사선학적 지표를 반복 측정해 관리 지표로 삼을지를 정리하면 다음과 같다.

| 질환군 | 추적 지표(X-ray 기반) | 촬영 간격의 일반 원칙 | 병행 지표(비영상) |
| --- | --- | --- | --- |
| 척추 정렬·퇴행성 척추질환 | 추간판 높이, 골극 형성 정도, 척추전방전위증 진행 여부 | 증상 악화·수술 고려 시에만 재촬영 | VAS, ODI(Oswestry 기능장애지수) |
| 슬관절·고관절 골관절염 | Kellgren-Lawrence 등급, 관절간격 폭 | 1~2년 단위, 또는 증상 급변 시 | WOMAC, VAS, 보행거리 |
| 골다공증·척추압박골절 | DXA T-score, 척추체 형태계측 등급(반정량적 평가) | DXA는 통상 1~2년 간격, 급성 골절 의심 시 즉시 | 낙상력, FRAX 골절위험도 |
| 척추측만증 | Cobb각(가능하면 초음파로 보완) | 성장기에는 4~6개월~1년, 성장 종료 후에는 개별화 | 신장, 초경 여부(여아 성장 지표) |
| 경추·경부 질환 | 경추 시상면 정렬각(전만·후만), 추간판 높이 | 증상 변화·외상 시에만 재촬영 | NDI(경부장애지수), VAS |
| 골절·외상성 손상 | 골절선 유합 정도, 정복 후 정렬 | 정복 직후, 유합 확인 시점(수 주~수 개월) | 통증 점수, 기능 회복 정도 |
| 천장관절·척추관절병증 | 천장관절 미란·경화·유합 단계 | 염증 활동성 변화 시(보통 1~2년 간격) | BASDAI, BASFI, CRP·ESR |

이 표는 임상 틀이지 동일 근거수준의 권고가 아니다. 실제 추적 간격은 개별 환자의 위험도·증상 변화·방사선 안전성(제5편)을 종합해 결정해야 하며, 특히 성장기·가임기 환자에서는 불필요한 반복 촬영을 피하는 것이 우선한다.

**변증 층화 강조**: 위 4-1~4-8의 모든 질환군에서, 방사선학적 등급(K-L 등급, Cobb각, 척추골절 등급 등)은 치료 강도·기법을 자동으로 결정하는 지표가 아니다. 변증 없는 관행적 취혈/처방은 근거에 부합하지 않으며, 반드시 통증 양상·설맥·전신 상태를 종합한 변증에 따라 치법을 선택해야 한다.

---

## 제5편 안전성

### 5-1. 방사선 피폭선량

단순 방사선 검사의 실효선량은 부위별로 크게 다르며, 흉부 후전방 촬영은 약 0.02 mSv, 요추 촬영은 약 0.7~1.5 mSv 내외로 알려져 있다(장비·기법에 따라 변동)[교과서적 근거]. 진단영상의학의 환자 선량학 문헌은 촬영 기법·장비 세대에 따라 동일 부위에서도 선량이 수배 차이 날 수 있음을 강조하며, ALARA(As Low As Reasonably Achievable) 원칙에 따라 임상적으로 필요한 최소 선량으로 영상을 획득해야 한다고 정리한다[^91]. 진단영상 장비 자체의 물리적 특성(관전압·필터·검출기 감도)이 선량-화질 균형에 미치는 영향도 함께 다룬다[^92].

| 부위 | 대략적 실효선량 | 비고 |
| --- | --- | --- |
| 흉부(PA) | 약 0.02 mSv | 자연방사선 약 3일분에 해당 |
| 요추(AP+측면) | 약 0.7~1.5 mSv | 복부 CT(약 8 mSv) 대비 현저히 낮음 |
| 경추 | 약 0.08 mSv | |
| 골반 | 약 0.6~0.7 mSv | |
| 슬관절·손목·발목 | 0.001 mSv 미만 | 사지 말단부는 피폭이 매우 낮음 |

이 표의 수치는 대표값이며, 실제 선량은 장비·기법·환자 체형에 따라 달라질 수 있어 개별 시설의 선량 관리 지표를 참조해야 한다[^91]. 이 표는 임상 틀이지 동일 근거수준의 권고가 아니다.

### 5-2. 직업적 피폭 관리

의료인의 직업적 방사선 피폭 관리도 중요한 안전성 항목이다. 한국 치과의사를 대상으로 한 조사에서 촬영 절차별 선량 관리 실태가 보고되었으며, 이는 X선 발생 장비를 다루는 모든 의료직군에 적용 가능한 원칙(차폐·거리·시간 관리)을 시사한다[^63]. 한의사가 X-ray를 직접 촬영·판독하는 시설을 운영할 경우, 방사선 관계 종사자 안전관리 법령에 따른 정기적 피폭선량 측정·차폐 시설 기준 준수가 필요하다[교과서적 근거].

### 5-3. 소아 방사선 안전성

소아는 세포 분열이 활발하고 방사선에 대한 조직 감수성이 성인보다 높으며, 남은 기대수명이 길어 확률적 위해(암 발생 위험)가 누적될 시간도 길다는 점에서 성인보다 엄격한 선량 관리가 필요하다[교과서적 근거]. 청소년 특발성 척추측만증 추적관찰에서 반복 촬영에 따른 누적 피폭과 관련해, 척추측만증 환자군에서의 방사선 노출에 따른 암·사망 위험을 종합한 체계적 고찰·메타분석은 장기간 반복 촬영이 이루어지는 이 질환군에서 저선량 촬영 프로토콜과 대체 영상기법(초음파 Cobb각 측정 등) 도입의 필요성을 뒷받침한다[^8]. 소아 골밀도 평가에서도 체구가 작은 피검자에서의 DXA 측정 조건이 임상 측정치에 영향을 미친다는 연구가 있어[^104], 소아 특이적 프로토콜 적용의 중요성을 보여준다. 한국 소아청소년 골밀도 참조치 확립 연구도 소아 영상 검사의 체구별 보정 필요성을 뒷받침한다[^50].

### 5-4. 임신부 방사선 안전성

임신부의 복부·골반부 방사선 노출은 태아 피폭과 직결되므로 원칙적으로 임신이 확인되거나 의심되는 경우 비필수 방사선 촬영은 연기하거나 대체 영상기법(초음파·MRI)을 우선 고려한다[교과서적 근거]. 사지·흉부 등 태아와 거리가 먼 부위 촬영은 적절한 차폐(납 앞치마 등)를 시행하면 태아선량이 매우 낮게 유지될 수 있다는 것이 방사선 안전학의 일반 원칙이다[교과서적 근거]. 임신부에서 불가피하게 척추·골반 영상이 필요한 경우(외상, 마미증후군 의심 등)에는 방사선과 협진을 통해 최소 촬영 횟수·최적 차폐로 진행하며, 가능하면 MRI·초음파로 대체한다[교과서적 근거]. 이 항목은 직접적인 임신부 대상 근거 논문이 충분히 확보되지 않아, 방사선 안전학의 일반 원칙(ALARA)과 산과 영상 프로토콜에 기반해 서술했음을 밝힌다.

### 5-5. 안전성 요약표

| 위험 | 내용 | 참고 |
| --- | --- | --- |
| 성장기 반복 촬영 누적 피폭 | 척추측만증 등 장기 추적관찰 질환에서 암·사망 위험 상승 가능성 | 체계적 고찰·메타분석 [^8] |
| 소아 방사선 감수성 | 성인보다 높은 조직 감수성, 긴 기대여명에 따른 누적 위험 | 교과서적 근거, 소아 DXA 조건 연구 [^104] |
| 임신부 태아 피폭 | 복부·골반 촬영 시 태아 직접 피폭 우려 | 교과서적 근거(ALARA 원칙) |
| 직업적 피폭 | 반복 시술자의 누적 피폭 관리 필요 | 치과의사 대상 관찰연구 [^63] |
| 과잉 촬영 | 불필요한 촬영은 이득 없이 피폭만 가중 | 임상결정규칙 미적용 시 촬영률 상승 [^60] |

이 표는 임상 틀이지 동일 근거수준의 권고가 아니다. 개별 환자의 위험-이득 평가는 임상 상황에 따라 개별화해야 한다.

---

## 제6편 다른 영상 검사(초음파·CT·MRI)와의 비교·선택 기준

### 6-1. 초음파와의 비교

초음파는 방사선 피폭이 없고 실시간 동적 평가가 가능하다는 장점이 있어, 특히 소아·임신부·반복 추적관찰이 필요한 상황에서 단순 방사선의 대안 또는 보완으로 활용된다. 슬관절 골관절염에서 반정량적 초음파와 슬관절 방사선촬영, MRI의 진단 성능을 비교한 연구는 각 영상기법이 서로 다른 병리(골극·활막염 등)를 포착함을 보여, 상호 보완적 활용의 근거를 제시한다[^65]. 척추측만증에서 초음파 기반 Cobb각 측정법의 신뢰도·타당도 연구는 초음파가 방사선 촬영의 완전한 대체는 아니나 추적관찰 빈도를 늘리는 보완 수단으로 유용함을 시사한다[^36]. 소아·청소년 골절 진단에서 임상의가 시행하는 현장초음파의 정확도를 평가한 연구도 있다[^64]. 발목·발 골절 평가에서 컬러 도플러 초음파의 역동적 스캐닝을 병행한 증례도 보고되었다[^97]. 흉부 영역에서는 폐 초음파와 흉부 방사선촬영의 진단 성능을 비교한 다수의 연구가 있는데, 급성호흡곤란증후군 식별에서 두 기법을 비교한 연구들은 상황에 따라 초음파가 방사선촬영과 대등하거나 우수할 수 있음을 보고했고[^66][^69], 외상 환자의 기흉 검출에서 폐 초음파와 흉부방사선의 진단 성능을 비교한 메타분석도 발표되었다[^9]. 다만 근골격계에서 초음파는 술자 의존성이 크고 골 내부·심부 구조 평가에 제한적이라는 한계가 있다[교과서적 근거]. 척추 시술(경피적 나사못 고정 등)의 유도 영상으로 초음파 볼륨 내비게이션·O-arm 내비게이션·투시 X-ray 유도를 비교한 무작위 대조 임상시험은 각 기법이 정확도·수술시간 면에서 서로 다른 장단점을 가짐을 보여, 시술 유도 목적에서도 영상기법 선택이 상황에 따라 달라질 수 있음을 시사한다[^13].

### 6-2. CT와의 비교

CT는 단순 방사선보다 골 구조를 단면으로 정밀하게 평가할 수 있어, 복잡골절·잠복골절·미세골절 검출에 유리하다. 골다공증성 척추 종판 함몰을 방사선과 CT로 비교한 연구는 CT가 방사선에서 놓칠 수 있는 소견을 더 많이 검출함을 보고했다[^73]. 고관절 골다공증 선별에 CT를 기회적으로 활용하는 접근의 진단 정확도를 종합한 체계적 고찰도 있다[^2]. 반면 CT는 단순 방사선보다 피폭선량이 현저히 높아(복부 CT는 흉부 단순촬영의 수백 배), 골다공증 선별과 같은 반복 검사가 필요한 상황에서는 선량 부담이 큰 단점이 있다[교과서적 근거]. CT의 골밀도 정량화 활용에서 팬텀 없는 자동 보정 기법을 개발한 연구도 있다[^43].

### 6-3. MRI와의 비교

MRI는 연부조직·골수·신경근 평가에서 단순 방사선·CT보다 우수하며, 마미증후군·신경근병증·초기 골수염 등 응급 신경학적 소견이 있을 때 1차로 고려된다[교과서적 근거](상세 임상결정 기준은 `영상 진단 필수 근골격계 질환` 문서 참조). 초기 슬관절 골관절염에서 MRI로 검출된 이상소견과 임상 증상 간의 관계를 분석한 연구는 MRI가 방사선에서 보이지 않는 초기 병변(연골하 골수병변 등)을 포착할 수 있음을 시사한다[^18]. 퇴행성 경추 척수병증에서 새로운 영상 기법을 정리한 문헌 고찰도 MRI를 중심에 두면서도 단순 방사선이 정렬·불안정성 선별의 출발점임을 강조한다[^88]. 다만 MRI는 검사 시간이 길고 비용이 높으며 즉시 접근성이 떨어져, 모든 근골격계 통증에 1차로 사용하기는 어렵다는 것이 각 질환 문서(요통·척추관협착증 등)에서 공통으로 강조하는 원칙이다[교과서적 근거].

### 6-4. 영상기법 선택 기준 종합

| 상황 | 1차 선택 | 2차 선택 | 근거 한계 |
| --- | --- | --- | --- |
| 급성 외상, 골절 의심 | 단순 방사선 | 음성이나 강한 임상적 의심 시 CT | 임상결정규칙 적용 [^60][^61] |
| 만성 관절통, 퇴행성 변화 평가 | 단순 방사선(체중부하) | 증상-영상 불일치 시 MRI | K-L 등급-증상 불일치 보고 [^31] |
| 신경학적 결손 동반 척추통 | MRI | 응급 시 CT 대체 | 교과서적 근거 |
| 골밀도 정량 평가 | DXA(이중에너지 X-ray) | 기회적 CT 활용 | DXA 임상 활용 근거 다수 [^38][^39][^49] |
| 소아·임신부 반복 추적 | 초음파(가능한 경우) | 필요 시 저선량 방사선 | Cobb각 초음파 신뢰도 [^36] |
| 감염·종양 의심 | MRI(1차) | 단순 방사선은 선별용 보조 | 교과서적 근거 |

이 표는 임상 틀이지 동일 근거수준의 권고가 아니다. 실제 검사 선택은 환자의 임상 소견·접근성·비용을 종합해 개별화해야 한다.

---

## 제7편 Q&A

**Q1. 한의원에서 X-ray를 직접 촬영·판독해도 되는가?**

한의사의 진단용 방사선 발생장치 사용 범위는 국내 법령·정책에 따라 규정되며, 이는 임상 근거의 문제가 아니라 제도적 사안이므로 개별 기관은 관할 보건당국의 최신 지침을 확인해야 한다. 방사선 장비를 다루는 경우 방사선 관계 종사자 안전관리 기준(정기 피폭선량 측정, 차폐시설 등)을 반드시 준수해야 한다[^63][^91].

**Q2. 방사선 소견이 정상이면 통증의 원인이 없다는 뜻인가?**

아니다. 진행성 방사선학적 슬관절 골관절염이 있어도 통증이 없는 경우가 상당수 보고되며[^31], 반대로 방사선이 정상이어도 근막통증증후군·조기 골관절염(연골하 골수병변 등 MRI 소견)처럼 통증이 있을 수 있다[^18]. 방사선 소견과 임상 증상은 독립적으로 평가해야 하며, 치료 결정은 증상·기능 상태·변증을 기준으로 한다.

**Q3. 추나 시행 전 반드시 X-ray를 찍어야 하는가?**

레드플래그(외상력, 진행성 신경학적 결손, 발열, 암 병력 등)가 없는 전형적 근골격계 통증은 X-ray 없이 촉진·이학적 검사만으로 보존치료를 시작할 수 있다는 것이 다수 임상진료지침의 공통 원칙이다(상세는 `영상 진단 필수 근골격계 질환` 문서 참조). 다만 강한 추나 수기를 계획하거나 고령·골다공증 위험군, 경추부 고강도 수기를 고려하는 경우에는 골절·불안정성을 배제하기 위한 사전 영상 확인이 안전에 기여할 수 있다[교과서적 근거]. 촉진·X-ray·AI 판독 프로그램 간 일치도를 분석한 연구는 촉진 소견과 영상 소견이 완전히 일치하지는 않음을 보여, 촉진만으로 모든 구조적 이상을 대체 판단하기 어려움을 시사한다[^57][^58].

**Q4. 척추측만증 소아 환자는 얼마나 자주 X-ray를 찍어야 하는가?**

촬영 간격은 성장 속도·측만 각도 진행 여부에 따라 개별화되며, 과도한 반복 촬영은 누적 피폭 위험을 높일 수 있다[^8]. 초음파 기반 Cobb각 측정이 표준 방사선 측정과 높은 상관관계를 보인다는 연구는[^36], 추나 등 한방치료를 병행하며 자주 경과를 확인해야 하는 환자에서 초음파를 보완적으로 활용해 방사선 촬영 빈도를 줄이는 전략의 근거가 된다.

**Q5. DXA(골밀도 검사)도 X-ray의 일종인가?**

그렇다. DXA는 이중 에너지의 X선을 이용해 골밀도를 정량화하는 특수한 형태의 X-ray 검사로, 일반 단순촬영보다 피폭선량이 훨씬 낮다[교과서적 근거]. 한국인 골밀도 참조치[^49][^50], DXA 측정 프로토콜 검증 연구[^44][^53] 등이 임상 활용의 근거를 뒷받침한다. 골다공증성 압박골절이 의심되는 요통 환자에서는 단순 방사선(척추체 형태 확인)과 DXA(정량적 골밀도)를 함께 고려하는 것이 근거에 부합한다[^84].

**Q6. AI가 X-ray를 판독해주면 한의사의 판독 역량은 필요 없는가?**

아니다. AI 보조판독 도구는 K-L 등급 판정 등에서 우수한 성능을 보이지만[^6][^35], 이는 어디까지나 보조 도구로서의 근거이며 최종 판독·임상적 통합 해석은 여전히 판독자(영상의학과 전문의, 또는 관련 법령이 허용하는 범위 내의 임상의)의 몫이다. 류마티스내과 영역의 AI 개관 문헌도 임상 통합 시 해석가능성과 검증의 중요성을 강조한다[^89]. 한의사가 영상 소견을 이해하고 변증·치료 결정에 통합하는 기초 판독 역량은 AI 도구 유무와 무관하게 필요하다.

**Q7. 흉부 X-ray와 근골격계 X-ray는 판독 원리가 다른가?**

기본 물리 원리(감약 차이에 따른 대조도 형성)는 동일하나, 관심 대상 조직의 대조도 특성이 달라 촬영 기법(관전압·필터)이 다르게 최적화된다[^91][^92]. 흉부는 폐야의 공기-연부조직 대조를 살리는 고kVp 기법을, 골격계는 골-연부조직 대조를 살리는 저~중 kVp 기법을 사용하는 경향이 있다[교과서적 근거]. 판독 시에도 흉부는 폐야·종격동·심장 실루엣을 중심으로, 근골격계는 ABCS(정렬-골밀도-관절간격-연부조직) 원칙을 중심으로 접근한다는 점에서 체계가 다르다.

---

## 근거의 한계

본 문서에서 인용한 근거의 상당수는 슬관절·고관절 골관절염의 K-L 등급, 척추 압박골절의 반정량적 평가, DXA 기반 골다공증 진단 등 특정 영상 지표의 타당도·유병률·AI 보조판독 성능을 다룬 관찰연구·실험연구로, 무작위 대조 임상시험 수준의 개입 효과 근거는 상대적으로 적다. 임신부 방사선 안전성에 대해서는 직접적인 인체 대상 연구가 충분히 검색되지 않아 방사선 안전학의 일반 원칙(ALARA)에 근거해 서술했다. 흉부 방사선 판독·AI 관련 근거는 근골격계가 아닌 흉부질환 검출 연구가 다수이나, 촬영 원리·판독 체계·AI 보조판독의 일반 원칙을 설명하는 데 참고자료로 활용했다. 한의학 고유 치료(침구·본초·추나)와 영상 소견의 직접적 상관을 다룬 근거는 추나 변증-영상 일치도 연구[^57][^58] 등으로 제한적이며, 향후 이 접점의 근거 축적이 더 필요하다.

---

> **환자 설명용 요약**: X-ray(단순 방사선 검사, 흔히 "엑스레이"라 부르는 검사)는 뼈의 모양과 관절 간격을 짧은 시간에 확인할 수 있는 안전한 검사입니다. 한 번 촬영으로 받는 방사선량은 매우 적어서(가슴 사진 한 장은 자연 상태에서 며칠 동안 받는 방사선량과 비슷한 수준입니다), 필요할 때 의사의 판단에 따라 촬영하는 것은 걱정할 만한 위험이 아닙니다. 다만 뼈의 사진에서 "이상 소견"이 보인다고 해서 반드시 그것이 통증의 원인이라는 뜻은 아니며, 반대로 사진이 깨끗해도 통증이 있을 수 있습니다. 그래서 한의사는 사진 소견과 함께 환자분이 느끼는 증상, 맥과 혀의 상태(변증)를 종합해서 치료 방향을 정합니다. 성장기 자녀가 척추측만증으로 자주 추적 검사를 받아야 한다면, 방사선 없는 초음파 검사로 대체하거나 촬영 간격을 조절하는 방법을 담당 의료진과 상의할 수 있습니다.

---

**고전 인용 출처**: 『黃帝內經素問』(五藏生成篇, 痿論), 『靈樞』(經脈, 骨度), 『難經』 — 신주골(腎主骨)·간주근(肝主筋) 이론은 위 원전의 장부-형체 상관 이론에 근거한 교과서적 서술이다.

**문헌 데이터 출처**: [한의학 논문 데이터베이스 (med.symbolicinfo.com)](https://med.symbolicinfo.com) — 2026-08-25 조회 기준

---

[^1]: Variations in the prevalence of scoliosis by age, sex, geographic region, and subtype among Chinese children: A systematic review and modelling study. Cao J 외. _Journal of global health_. 2024-04-12. [체계적 고찰] [DOI 10.7189/jogh.14.04062](https://doi.org/10.7189/jogh.14.04062) [PMID 42370398](https://pubmed.ncbi.nlm.nih.gov/42370398/) — 청소년 특발성 척추측만증의 역학·추적관찰에서 X-ray 활용 근거.
[^2]: Opportunistic CT-based osteoporosis screening of the hip: a systematic review of diagnostic accuracy. Vermue H 외. _Archives of orthopaedic and trauma surgery_. 2025-11-18. [체계적 고찰] [DOI 10.1007/s00402-025-06130-1](https://doi.org/10.1007/s00402-025-06130-1) [PMID 41251840](https://pubmed.ncbi.nlm.nih.gov/41251840/) — 기회적 CT 골다공증 선별의 진단 정확도, X-ray/DXA와의 비교 근거.
[^3]: A scoping review on the application of new technology in the screening and diagnosis of adolescent idiopathic scoliosis. Dulani N 외. _Spine deformity_. 2026-08-11. [체계적 고찰] [DOI 10.1007/s43390-026-01517-5](https://doi.org/10.1007/s43390-026-01517-5) [PMID 42581262](https://pubmed.ncbi.nlm.nih.gov/42581262/) — 청소년 특발성 척추측만증 선별·진단 신기술 개관.
[^4]: Application of artificial intelligence in X-ray imaging analysis for knee arthroplasty: A systematic review. Zhang Z 외. _PloS one_. 2025. [체계적 고찰] [DOI 10.1371/journal.pone.0321104](https://doi.org/10.1371/journal.pone.0321104) [PMID 40333699](https://pubmed.ncbi.nlm.nih.gov/40333699/) — 슬관절 영역 AI 보조 X-ray 판독의 적용 범위 개관.
[^5]: A systematic review of diagnostic accuracy of vertebral fracture assessment (VFA) in postmenopausal women and elderly men. Lee JH 외. _Osteoporosis international_. 2016-05. [체계적 고찰] [DOI 10.1007/s00198-015-3436-z](https://doi.org/10.1007/s00198-015-3436-z) [PMID 26782682](https://pubmed.ncbi.nlm.nih.gov/26782682/) — DXA 기반 척추골절평가(VFA)의 진단 정확도 근거.
[^6]: The value of deep learning-based X-ray techniques in detecting and classifying K-L grades of knee osteoarthritis: a systematic review and meta-analysis. Zhao H 외. _European radiology_. 2025-01. [메타분석] [DOI 10.1007/s00330-024-10928-9](https://doi.org/10.1007/s00330-024-10928-9) [PMID 38997539](https://pubmed.ncbi.nlm.nih.gov/38997539/) — 슬관절 골관절염 K-L 등급 AI 자동판독의 진단 정확도 근거.
[^7]: The correlation between osteoporotic vertebrae fracture risk and bone mineral density measured by quantitative computed tomography and dual energy X-ray absorptiometry: a systematic review and meta-analysis. Chen L 외. _European spine journal_. 2023-11. [메타분석] [DOI 10.1007/s00586-023-07917-9](https://doi.org/10.1007/s00586-023-07917-9) [PMID 37740786](https://pubmed.ncbi.nlm.nih.gov/37740786/) — QCT와 DXA의 척추골절 위험 예측력 비교 근거.
[^8]: Cancer and mortality risks of patients with scoliosis from radiation exposure: a systematic review and meta-analysis. Luan FJ 외. _European spine journal_. 2020-12. [메타분석] [DOI 10.1007/s00586-020-06573-7](https://doi.org/10.1007/s00586-020-06573-7) [PMID 32852591](https://pubmed.ncbi.nlm.nih.gov/32852591/) — 척추측만증 반복촬영에 따른 누적 피폭과 암·사망 위험의 연관성 근거.
[^9]: Comparing the Diagnostic Performance of Lung Ultrasonography and Chest Radiography for Detecting Pneumothorax in Patients with Trauma: A Meta-Analysis. Sheng B 외. _Respiration_. 2025. [메타분석] [DOI 10.1159/000540777](https://doi.org/10.1159/000540777) [PMID 39348819](https://pubmed.ncbi.nlm.nih.gov/39348819/) — 외상 환자 기흉 검출에서 초음파-흉부 X-ray 진단 성능 비교 근거.
[^10]: ACR Appropriateness Criteria(®) Rib Fractures. Expert Panel on Thoracic Imaging 외. _Journal of the American College of Radiology_. 2019-05. [임상진료지침] [DOI 10.1016/j.jacr.2019.02.019](https://doi.org/10.1016/j.jacr.2019.02.019) [PMID 31054749](https://pubmed.ncbi.nlm.nih.gov/31054749/) — 늑골 골절 의심 시 단순촬영의 초기 평가 위치를 규정한 지침.
[^11]: Home exercise therapy to improve muscle strength and joint flexibility effectively treats pre-radiographic knee OA in community-dwelling elderly: a randomized controlled trial. Suzuki Y 외. _Clinical rheumatology_. 2019-01. [임상시험] [DOI 10.1007/s10067-018-4263-3](https://doi.org/10.1007/s10067-018-4263-3) [PMID 30167975](https://pubmed.ncbi.nlm.nih.gov/30167975/) — 방사선학적 변화 이전 단계에서도 증상 기준 보존치료가 유효함을 보인 임상시험.
[^12]: Clinical and radiographic outcomes of cervical disc replacement with a new prosthesis. Miao J 외. _The spine journal_. 2014-06-01. [임상시험] [DOI 10.1016/j.spinee.2013.07.439](https://doi.org/10.1016/j.spinee.2013.07.439) [PMID 24095101](https://pubmed.ncbi.nlm.nih.gov/24095101/) — 경추 정렬 방사선 지표를 결과변수로 사용한 임상시험 근거.
[^13]: A comparison of ultrasound volume navigation, O-arm navigation, and X-ray guidance for screw placement in minimally invasive transforaminal lumbar interbody fusion: a randomized controlled trial. Lin X 외. _European spine journal_. 2024-09. [임상시험] [DOI 10.1007/s00586-024-08390-8](https://doi.org/10.1007/s00586-024-08390-8) [PMID 38980367](https://pubmed.ncbi.nlm.nih.gov/38980367/) — 척추 시술 유도에서 초음파·X-ray 기법 간 비교 근거.
[^14]: Conventional Versus Artificial Intelligence-Assisted Interpretation of Chest Radiographs in Patients With Acute Respiratory Symptoms in Emergency Department: A Pragmatic Randomized Clinical Trial. Hwang EJ 외. _Korean journal of radiology_. 2023-03. [임상시험] [DOI 10.3348/kjr.2022.0651](https://doi.org/10.3348/kjr.2022.0651) [PMID 36788769](https://pubmed.ncbi.nlm.nih.gov/36788769/) — AI 보조판독과 기존 판독의 실용적 무작위 비교 근거.
[^15]: Effect of a two-hour training on physicians' skill in interpreting Pneumoconiotic chest radiographs. Ngatu NR 외. _Journal of occupational health_. 2010. [임상시험] [DOI 10.1539/joh.l10065](https://doi.org/10.1539/joh.l10065) [PMID 20697183](https://pubmed.ncbi.nlm.nih.gov/20697183/) — 짧은 훈련만으로도 판독 역량이 향상될 수 있음을 보인 근거.
[^16]: Safety and Efficacy of Bone Cement (Spinofill®) for Vertebroplasty in Patients with Osteoporotic Compression Fracture: A Preliminary Prospective Study. Park HB 외. _Journal of Korean Neurosurgical Society_. 2022-09. [임상시험] [DOI 10.3340/jkns.2022.0028](https://doi.org/10.3340/jkns.2022.0028) [PMID 35577757](https://pubmed.ncbi.nlm.nih.gov/35577757/) — 골다공증성 압박골절에서 척추성형술의 안전성·유효성 예비 근거.
[^17]: Defining the presence of radiographic knee osteoarthritis: a comparison between the Kellgren and Lawrence system and OARSI atlas criteria. Culvenor AG 외. _Knee surgery, sports traumatology, arthroscopy_. 2015-12. [관찰연구] [DOI 10.1007/s00167-014-3205-0](https://doi.org/10.1007/s00167-014-3205-0) [PMID 25079135](https://pubmed.ncbi.nlm.nih.gov/25079135/) — K-L 등급과 OARSI 아틀라스 기준 간 유병률 추정치 차이를 보인 핵심 근거.
[^18]: Relationship between abnormalities detected by magnetic resonance imaging and knee symptoms in early knee osteoarthritis. Ota S 외. _Scientific reports_. 2021-07-26. [관찰연구] [DOI 10.1038/s41598-021-94382-3](https://doi.org/10.1038/s41598-021-94382-3) [PMID 34312418](https://pubmed.ncbi.nlm.nih.gov/34312418/) — MRI가 X-ray보다 초기 병변을 더 민감하게 포착함을 시사하는 근거.
[^19]: Novel elemental grading system for radiographic lumbar spondylosis in a population based-cohort study of a Japanese mountain village. Yamada J 외. _PloS one_. 2022. [관찰연구] [DOI 10.1371/journal.pone.0270282](https://doi.org/10.1371/journal.pone.0270282) [PMID 35763521](https://pubmed.ncbi.nlm.nih.gov/35763521/) — 요추 척추증의 새로운 요소별 방사선학적 등급체계 근거.
[^20]: Serum pentosidine concentration is associated with radiographic severity of lumbar spondylosis in a general Japanese population. Chiba D 외. _Journal of bone and mineral metabolism_. 2017-01. [관찰연구] [DOI 10.1007/s00774-015-0727-6](https://doi.org/10.1007/s00774-015-0727-6) [PMID 26661661](https://pubmed.ncbi.nlm.nih.gov/26661661/) — 생화학 지표와 요추 방사선학적 중증도의 연관성 근거.
[^21]: Radiographic features of hand osteoarthritis in adult Kashin-Beck Disease (KBD): the Yongshou KBD study. Fu Q 외. _Osteoarthritis and cartilage_. 2015-06. [관찰연구] [DOI 10.1016/j.joca.2015.01.009](https://doi.org/10.1016/j.joca.2015.01.009) [PMID 25623625](https://pubmed.ncbi.nlm.nih.gov/25623625/) — 특정 지역성 골관절병의 수부 방사선 소견 근거.
[^22]: Prevalence of radiographic knee osteoarthritis in China: a national survey of thirty thousand, four hundred and fifty five individuals cross-sectional study. Lv H 외. _International orthopaedics_. 2025-10. [관찰연구] [DOI 10.1007/s00264-025-06643-9](https://doi.org/10.1007/s00264-025-06643-9) [PMID 40900168](https://pubmed.ncbi.nlm.nih.gov/40900168/) — 대규모 인구집단의 방사선학적 슬관절 골관절염 유병률 근거.
[^23]: Association between the distal tibiofibular syndesmosis morphology classification and ankle osteoarthritis: a retrospective study. Huang L 외. _Journal of orthopaedic surgery and research_. 2023-08-03. [관찰연구] [DOI 10.1186/s13018-023-03985-1](https://doi.org/10.1186/s13018-023-03985-1) [PMID 37537622](https://pubmed.ncbi.nlm.nih.gov/37537622/) — 발목 골관절염과 원위경비인대결합 형태 분류의 연관성 근거.
[^24]: Radiographic changes in the lumbar spine in former elite athletes. Schmitt H 외. _Spine_. 2004-11-15. [관찰연구] [DOI 10.1097/01.brs.0000145606.68189.69](https://doi.org/10.1097/01.brs.0000145606.68189.69) [PMID 15543073](https://pubmed.ncbi.nlm.nih.gov/15543073/) — 반복적 기계적 부하와 요추 방사선학적 변화의 연관성 근거.
[^25]: Distribution of coronal plane alignment of the knee classification in Chinese osteoarthritic and healthy population: a retrospective cross-sectional observational study. Gao YH 외. _International journal of surgery_. 2024-05-01. [관찰연구] [DOI 10.1097/JS9.0000000000001178](https://doi.org/10.1097/JS9.0000000000001178) [PMID 38349219](https://pubmed.ncbi.nlm.nih.gov/38349219/) — 관상면 정렬(CPAK) 분류의 인구집단별 분포 근거.
[^26]: Coronal Plane Alignment of the Knee (CPAK) Type Shifts Toward Constitutional Varus with Increasing Kellgren and Lawrence Grade: A Radiographic Analysis of 17,365 Knees. Kim SE 외. _The Journal of bone and joint surgery. American volume_. 2025-02-05. [관찰연구] [DOI 10.2106/JBJS.24.00316](https://doi.org/10.2106/JBJS.24.00316) [PMID 39719004](https://pubmed.ncbi.nlm.nih.gov/39719004/) — K-L 등급 증가에 따른 관상면 정렬 변화의 대규모 방사선 분석 근거.
[^27]: Dynamic changes to the tibiofemoral joint line with increasing osteoarthritis severity and its relationship to constitutional alignment: a radiological analysis of 3,320 knees. Farey JE 외. _Bone & joint open_. 2026-02-19. [관찰연구] [DOI 10.1302/2633-1462.72.BJO-2025-0370.R1](https://doi.org/10.1302/2633-1462.72.BJO-2025-0370.R1) [PMID 41707681](https://pubmed.ncbi.nlm.nih.gov/41707681/) — 골관절염 중증도에 따른 관절선 변화의 방사선 분석 근거.
[^28]: Coronal alignment parameters of the knee predict osteoarthritis development: a Coronal Plane Alignment of the Knee classification-based analysis using the Multicenter Osteoarthritis Study data. Kim JS 외. _The bone & joint journal_. 2026-07-01. [관찰연구] [DOI 10.1302/0301-620X.108B7.BJJ-2025-0687.R2](https://doi.org/10.1302/0301-620X.108B7.BJJ-2025-0687.R2) [PMID 42379578](https://pubmed.ncbi.nlm.nih.gov/42379578/) — 관상면 정렬 지표가 골관절염 발생을 예측한다는 코호트 근거.
[^29]: The pre-diseased coronal alignment can be predicted from conventional radiographs taken of the varus arthritic knee. Colyn W 외. _Archives of orthopaedic and trauma surgery_. 2023-07. [관찰연구] [DOI 10.1007/s00402-022-04709-6](https://doi.org/10.1007/s00402-022-04709-6) [PMID 36494462](https://pubmed.ncbi.nlm.nih.gov/36494462/) — 통상 방사선촬영에서 병전 정렬을 역산할 수 있다는 근거.
[^30]: Correlation between radiographic knee osteoarthritis and lifetime cigarette smoking amount in a Korean population: A cross-sectional study. Kim JW 외. _Medicine_. 2020-06-26. [관찰연구] [DOI 10.1097/MD.0000000000020839](https://doi.org/10.1097/MD.0000000000020839) [PMID 32590777](https://pubmed.ncbi.nlm.nih.gov/32590777/) — 흡연량과 방사선학적 슬관절 골관절염의 연관성 근거.
[^31]: Absence of pain in subjects with advanced radiographic knee osteoarthritis. Son KM 외. _BMC musculoskeletal disorders_. 2020-09-29. [관찰연구] [DOI 10.1186/s12891-020-03647-x](https://doi.org/10.1186/s12891-020-03647-x) [PMID 32993609](https://pubmed.ncbi.nlm.nih.gov/32993609/) — 방사선 소견과 통증 증상이 불일치할 수 있음을 보인 핵심 근거.
[^32]: Association between metabolic syndrome and radiographic spine osteoarthritis: Cross-sectional analysis using data from the Korea National Health and Nutrition Examination Survey. Kim SK 외. _International journal of rheumatic diseases_. 2022-04. [관찰연구] [DOI 10.1111/1756-185X.14296](https://doi.org/10.1111/1756-185X.14296) [PMID 35092627](https://pubmed.ncbi.nlm.nih.gov/35092627/) — 대사증후군과 척추 방사선학적 골관절염의 연관성 근거.
[^33]: Knee osteoarthritis with a high grade of Kellgren-Lawrence score is associated with a worse frailty status, KNHANES 2010-2013. Joo SH 외. _Scientific reports_. 2023-11-12. [관찰연구] [DOI 10.1038/s41598-023-46558-2](https://doi.org/10.1038/s41598-023-46558-2) [PMID 37953320](https://pubmed.ncbi.nlm.nih.gov/37953320/) — K-L 등급과 노쇠 지표의 연관성 근거.
[^34]: The prevalence of and demographic factors associated with radiographic knee osteoarthritis in Korean adults aged ≥ 50 years: The 2010-2013 Korea National Health and Nutrition Examination Survey. Hong JW 외. _PloS one_. 2020. [관찰연구] [DOI 10.1371/journal.pone.0230613](https://doi.org/10.1371/journal.pone.0230613) [PMID 32196540](https://pubmed.ncbi.nlm.nih.gov/32196540/) — 한국 성인의 방사선학적 슬관절 골관절염 유병률·연관 요인 근거.
[^35]: Performance of an Artificial Intelligence-Based Software for Automated Kellgren-Lawrence Grading of Knee Osteoarthritis: A Multicenter Cohort Study. Choi BS 외. _The Journal of arthroplasty_. 2026-02-04. [관찰연구] [DOI 10.1016/j.arth.2026.01.078](https://doi.org/10.1016/j.arth.2026.01.078) [PMID 41651085](https://pubmed.ncbi.nlm.nih.gov/41651085/) — AI 자동 K-L 등급 소프트웨어의 다기관 검증 근거.
[^36]: Radiation-free Assessment of Scoliosis: A Reliability and Validity Study for Ultrasound Angles. Zhu S 외. _Global spine journal_. 2026-07-06. [관찰연구] [DOI 10.1177/21925682261466587](https://doi.org/10.1177/21925682261466587) [PMID 42403061](https://pubmed.ncbi.nlm.nih.gov/42403061/) — 초음파 Cobb각 측정의 신뢰도·타당도, 방사선 대체·보완 근거.
[^38]: Predictive ability of novel volumetric and geometric indices derived from dual-energy X-ray absorptiometric images of the proximal femur for hip fracture compared with conventional areal bone mineral density: the Japanese Population-based Osteoporosis (JPOS) Cohort Study. Iki M 외. _Osteoporosis international_. 2021-11. [관찰연구] [DOI 10.1007/s00198-021-06013-2](https://doi.org/10.1007/s00198-021-06013-2) [PMID 34041560](https://pubmed.ncbi.nlm.nih.gov/34041560/) — DXA 유래 부가 지표가 고관절골절 예측에 기여함을 보인 근거.
[^39]: Intervals between bone mineral density testing with dual-energy X-ray absorptiometry scans in clinical practice. Lyu H 외. _Osteoporosis international_. 2019-04. [관찰연구] [DOI 10.1007/s00198-019-04847-5](https://doi.org/10.1007/s00198-019-04847-5) [PMID 30680429](https://pubmed.ncbi.nlm.nih.gov/30680429/) — 실제 임상에서 DXA 재검 간격 실태를 보인 근거.
[^43]: Automatic phantom-less calibration of routine CT scans for the evaluation of osteoporosis and hip fracture risk. Li W 외. _Bone_. 2025-05. [관찰연구] [DOI 10.1016/j.bone.2025.117431](https://doi.org/10.1016/j.bone.2025.117431) [PMID 40015421](https://pubmed.ncbi.nlm.nih.gov/40015421/) — CT의 골밀도 정량화 활용, 팬텀 없는 자동 보정 기법 근거.
[^44]: Measurements of bone mineral density in the lumbar spine and proximal femur using lunar prodigy and the new pencil-beam dual-energy X-ray absorptiometry. Choi D 외. _Skeletal radiology_. 2010-11. [관찰연구] [DOI 10.1007/s00256-009-0828-1](https://doi.org/10.1007/s00256-009-0828-1) [PMID 19924413](https://pubmed.ncbi.nlm.nih.gov/19924413/) — DXA 측정 프로토콜(펜슬빔 방식)의 검증 근거.
[^46]: Comparison of the prevalence of osteoporosis in people with spinal cord injury according to bone mineral density reference values for the diagnosis of osteoporosis: a retrospective, cross-sectional study. Lim J 외. _BMC musculoskeletal disorders_. 2024-01-26. [관찰연구] [DOI 10.1186/s12891-024-07184-9](https://doi.org/10.1186/s12891-024-07184-9) [PMID 38279100](https://pubmed.ncbi.nlm.nih.gov/38279100/) — 척추손상 환자에서 DXA 기준별 골다공증 유병률 추정 차이 근거.
[^49]: Prevalence of osteoporosis and reference data for lumbar spine and hip bone mineral density in a Korean population. Cui LH 외. _Journal of bone and mineral metabolism_. 2008. [관찰연구] [DOI 10.1007/s00774-007-0847-8](https://doi.org/10.1007/s00774-007-0847-8) [PMID 18979161](https://pubmed.ncbi.nlm.nih.gov/18979161/) — 한국인 요추·고관절 골밀도 참조치 근거.
[^50]: Reference values for bone mineral density according to age with body size adjustment in Korean children and adolescents. Yi KH 외. _Journal of bone and mineral metabolism_. 2014-05. [관찰연구] [DOI 10.1007/s00774-013-0488-z](https://doi.org/10.1007/s00774-013-0488-z) [PMID 23832576](https://pubmed.ncbi.nlm.nih.gov/23832576/) — 한국 소아청소년 체구보정 골밀도 참조치 근거.
[^52]: Spine age derived from DXA vertebral fracture assessment images predicts incident fractures and mortality: the Manitoba Bone Mineral Density Registry. Cho SW 외. _Journal of bone and mineral research_. 2026-02-03. [관찰연구] [DOI 10.1093/jbmr/zjaf194](https://doi.org/10.1093/jbmr/zjaf194) [PMID 41408721](https://pubmed.ncbi.nlm.nih.gov/41408721/) — DXA VFA 영상 기반 "척추 나이"의 예후 예측력 근거.
[^53]: A Novel Dual-Energy X-Ray Absorptiometry Protocol for the Proximal Humerus Reveals a Fatty Infiltration Dependent Reduction in Bone Mineral Density. Cho JW 외. _Journal of orthopaedic research_. 2026-04. [관찰연구] [DOI 10.1002/jor.70187](https://doi.org/10.1002/jor.70187) [PMID 41914810](https://pubmed.ncbi.nlm.nih.gov/41914810/) — 근위 상완골 DXA 프로토콜 개발·검증 근거.
[^54]: The significant relationship among the factors of pelvic incidence, standing lumbar lordosis, and lumbar flexibility in Japanese patients with hip osteoarthritis: A descriptive radiographic study. Kobayashi T 외. _Orthopaedics & traumatology, surgery & research_. 2022-04. [관찰연구] [DOI 10.1016/j.otsr.2021.103123](https://doi.org/10.1016/j.otsr.2021.103123) [PMID 34700058](https://pubmed.ncbi.nlm.nih.gov/34700058/) — 서있는 자세 요추-골반 정렬 지표 간 상관관계 근거.
[^56]: Prevalence and Risk Factors of T-Score Spine-Hip Discordance in Patients with Osteoporotic Vertebral Compression Fracture. Yoon BH 외. _Journal of bone metabolism_. 2022-02. [관찰연구] [DOI 10.11005/jbm.2022.29.1.43](https://doi.org/10.11005/jbm.2022.29.1.43) [PMID 35325982](https://pubmed.ncbi.nlm.nih.gov/35325982/) — 척추-고관절 T-score 불일치의 빈도·위험요인 근거.
[^57]: Comparison of concordance between chuna manual therapy diagnosis methods (palpation, X-ray, artificial intelligence program) in lumbar spine. Jin-Hyun Lee 외. _Medicine_. 2021-12-23. [관찰연구] [DOI 10.1097/md.0000000000028177](https://doi.org/10.1097/md.0000000000028177) — 추나 변증에서 촉진·X-ray·AI 판독 간 일치도에 대한 근거.
[^58]: Comparison of Concordance between Chuna Manual Therapy Diagnostic Methods (Palpation, X-ray, Artificial Intelligence Program) in Lumbar Spine: An Exploratory, Cross-Sectional Clinical Study. Jin-Hyun Lee 외. _Diagnostics_. 2022-11-08. [관찰연구] [DOI 10.3390/diagnostics12112732](https://doi.org/10.3390/diagnostics12112732) — 위 연구의 확장·심화 분석으로, 추나 진단법 간 일치도의 임상적 함의를 다룸.
[^60]: Clinical value of the Ottawa ankle rules for diagnosis of fractures in acute ankle injuries. Wang X 외. _PloS one_. 2013. [관찰연구] [DOI 10.1371/journal.pone.0063228](https://doi.org/10.1371/journal.pone.0063228) [PMID 23646202](https://pubmed.ncbi.nlm.nih.gov/23646202/) — 오타와발목규칙의 골절 진단 민감도·촬영률 감소 효과 근거.
[^61]: Ottawa ankle and foot rules in China: applicability in a defensive environment. Jia CQ 외. _European journal of medical research_. 2025-07-30. [관찰연구] [DOI 10.1186/s40001-025-02961-1](https://doi.org/10.1186/s40001-025-02961-1) [PMID 40739246](https://pubmed.ncbi.nlm.nih.gov/40739246/) — 오타와규칙의 타문화권 적용 가능성 근거.
[^62]: Enteropathic arthritis in the sacroiliac joint. Imaging and differential diagnosis. Mester AR 외. _European journal of radiology_. 2000-09. [관찰연구] [DOI 10.1016/s0720-048x(00)00243-6](https://doi.org/10.1016/s0720-048x(00)00243-6) [PMID 11000563](https://pubmed.ncbi.nlm.nih.gov/11000563/) — 장병성 관절병증의 천장관절 영상 소견과 감별진단 근거.
[^63]: Occupational radiation procedures and doses in South Korean dentists. Kim YJ 외. _Community dentistry and oral epidemiology_. 2016-10. [관찰연구] [DOI 10.1111/cdoe.12237](https://doi.org/10.1111/cdoe.12237) [PMID 27146959](https://pubmed.ncbi.nlm.nih.gov/27146959/) — 방사선 장비를 다루는 의료직군의 직업적 피폭 관리 실태 근거.
[^64]: Accuracy of clinician-performed point-of-care ultrasound for the diagnosis of fractures in children and young adults. Weinberg ER 외. _Injury_. 2010-08. [관찰연구] [DOI 10.1016/j.injury.2010.04.020](https://doi.org/10.1016/j.injury.2010.04.020) [PMID 20466368](https://pubmed.ncbi.nlm.nih.gov/20466368/) — 소아·청소년 골절 진단에서 현장초음파의 정확도 근거.
[^65]: Comparison of Diagnostic Performance of Semi-Quantitative Knee Ultrasound and Knee Radiography with MRI: Oulu Knee Osteoarthritis Study. Podlipská J 외. _Scientific reports_. 2016-03-01. [관찰연구] [DOI 10.1038/srep22365](https://doi.org/10.1038/srep22365) [PMID 26926836](https://pubmed.ncbi.nlm.nih.gov/26926836/) — 초음파·X-ray·MRI의 슬관절 병리 검출 성능 비교 근거.
[^66]: Pulmonary ultrasound and pulse oximetry versus chest radiography and arterial blood gas analysis for the diagnosis of acute respiratory distress syndrome: a pilot study. Bass CM 외. _Critical care_. 2015-07-21. [관찰연구] [DOI 10.1186/s13054-015-0995-5](https://doi.org/10.1186/s13054-015-0995-5) [PMID 26325623](https://pubmed.ncbi.nlm.nih.gov/26325623/) — 초음파와 흉부방사선의 급성호흡곤란증후군 진단 성능 비교 근거.
[^67]: Increasing radiology capacity within the lung cancer pathway: centralised work-based support for trainee chest X-ray reporting radiographers. Woznitza N 외. _Journal of medical radiation sciences_. 2018-09. [관찰연구] [DOI 10.1002/jmrs.285](https://doi.org/10.1002/jmrs.285) [PMID 29806102](https://pubmed.ncbi.nlm.nih.gov/29806102/) — 방사선사 훈련을 통한 흉부 X-ray 판독 역량 확충 근거.
[^69]: Chest radiography versus lung ultrasound for identification of acute respiratory distress syndrome: a retrospective observational study. See KC 외. _Critical care_. 2018-08-18. [관찰연구] [DOI 10.1186/s13054-018-2105-y](https://doi.org/10.1186/s13054-018-2105-y) [PMID 30119687](https://pubmed.ncbi.nlm.nih.gov/30119687/) — 흉부방사선-초음파의 급성호흡곤란증후군 식별 비교 근거.
[^70]: [Clinical evaluation of Fuji computed radiography (FCR) by physicians including non-radiologists]. Akita S 외. _Rinsho hoshasen_. 1990-04. [관찰연구] [PMID 2355649](https://pubmed.ncbi.nlm.nih.gov/2355649/) — 초기 컴퓨터 방사선촬영(CR)의 임상 평가, 디지털 방사선촬영 역사의 근거.
[^73]: CT detects more osteoporotic endplate depressions than radiograph: a descriptive comparison of 76 vertebrae. Du EZ 외. _Osteoporosis international_. 2022-07. [관찰연구] [DOI 10.1007/s00198-022-06391-1](https://doi.org/10.1007/s00198-022-06391-1) [PMID 35368223](https://pubmed.ncbi.nlm.nih.gov/35368223/) — CT가 X-ray보다 특정 척추 소견을 더 많이 검출함을 보인 위음성 관련 근거.
[^75]: Assessment of the Suitability of the Fleischner Society Imaging Guidelines in Evaluating Chest Radiographs of COVID-19 Patients. Shin HJ 외. _Journal of Korean medical science_. 2023-07-03. [관찰연구] [DOI 10.3346/jkms.2023.38.e199](https://doi.org/10.3346/jkms.2023.38.e199) [PMID 37401494](https://pubmed.ncbi.nlm.nih.gov/37401494/) — 표준 판독 가이드라인 적용성 평가 근거.
[^76]: Added Value of Bone Suppression Image in the Detection of Subtle Lung Lesions on Chest Radiographs with Regard to Reader's Expertise. Hong GS 외. _Journal of Korean medical science_. 2019-10-07. [관찰연구] [DOI 10.3346/jkms.2019.34.e250](https://doi.org/10.3346/jkms.2019.34.e250) [PMID 31583870](https://pubmed.ncbi.nlm.nih.gov/31583870/) — 판독자 숙련도별 미세 병변 검출력 차이, 골 억제 후처리 영상의 보조 효과 근거.
[^77]: Ossification of the Medial Clavicular Epiphysis on Chest Radiographs: Utility and Diagnostic Accuracy in Identifying Korean Adolescents and Young Adults under the Age of Majority. Yoon SH 외. _Journal of Korean medical science_. 2016-10. [관찰연구] [DOI 10.3346/jkms.2016.31.10.1538](https://doi.org/10.3346/jkms.2016.31.10.1538) [PMID 27550480](https://pubmed.ncbi.nlm.nih.gov/27550480/) — 정상 발달 변이(쇄골 골단 골화)를 병변과 감별하는 판독 근거.
[^79]: Much lower prevalence and severity of radiographic osteoporotic vertebral fracture in elderly Hong Kong Chinese women than in age-matched Rome Caucasian women: a cross-sectional study. Wáng YXJ 외. _Archives of osteoporosis_. 2021-11-16. [관찰연구] [DOI 10.1007/s11657-021-00987-6](https://doi.org/10.1007/s11657-021-00987-6) [PMID 34783904](https://pubmed.ncbi.nlm.nih.gov/34783904/) — 인종·지역 간 척추골절 방사선 유병률 차이 근거.
[^80]: Differences in prevalence and associated factors between mild and severe vertebral fractures in Japanese men and women: the third survey of the ROAD study. Horii C 외. _Journal of bone and mineral metabolism_. 2019-09. [관찰연구] [DOI 10.1007/s00774-018-0981-5](https://doi.org/10.1007/s00774-018-0981-5) [PMID 30607619](https://pubmed.ncbi.nlm.nih.gov/30607619/) — 경도·중등도 척추골절의 연관요인 차이 근거.
[^81]: Comparison of expert and nonexpert physicians in the assessment of vertebral fractures using the semiquantitative method in Japan. Uemura Y 외. _Journal of bone and mineral metabolism_. 2015-11. [관찰연구] [DOI 10.1007/s00774-014-0625-3](https://doi.org/10.1007/s00774-014-0625-3) [PMID 25300745](https://pubmed.ncbi.nlm.nih.gov/25300745/) — 숙련도별 반정량적 척추골절 판독 일치도 근거.
[^82]: Prevalent vertebral fractures predict subsequent radiographic vertebral fractures in postmenopausal Korean women receiving antiresorptive agent. Kim SH 외. _Osteoporosis international_. 2011-03. [관찰연구] [DOI 10.1007/s00198-010-1298-y](https://doi.org/10.1007/s00198-010-1298-y) [PMID 20533028](https://pubmed.ncbi.nlm.nih.gov/20533028/) — 기존 척추골절이 향후 골절 위험을 예측함을 보인 근거.
[^84]: The importance of morphometric radiographic vertebral assessment for the detection of patients who need pharmacological treatment of osteoporosis among postmenopausal diabetic Korean women. Choi YJ 외. _Osteoporosis international_. 2012-08. [관찰연구] [DOI 10.1007/s00198-011-1803-y](https://doi.org/10.1007/s00198-011-1803-y) [PMID 21975560](https://pubmed.ncbi.nlm.nih.gov/21975560/) — 척추체 형태계측 평가가 약물치료 대상자 선별에 중요함을 보인 근거.
[^85]: Practical use of bone scan in patients with an osteoporotic vertebral compression fracture. Jun DS 외. _Journal of Korean medical science_. 2015-02. [관찰연구] [DOI 10.3346/jkms.2015.30.2.194](https://doi.org/10.3346/jkms.2015.30.2.194) [PMID 25653492](https://pubmed.ncbi.nlm.nih.gov/25653492/) — 척추압박골절 급성기 판정에서 골스캔의 실용적 가치 근거.
[^86]: Evaluating the role of surface topography in the surveillance of scoliosis. Applebaum A 외. _Spine deformity_. 2020-06. [문헌 고찰] [DOI 10.1007/s43390-019-00001-7](https://doi.org/10.1007/s43390-019-00001-7) [PMID 31965557](https://pubmed.ncbi.nlm.nih.gov/31965557/) — 방사선 무노출 표면지형 기법의 척추측만증 추적관찰 역할 개관.
[^88]: New Imaging Modalities for Degenerative Cervical Myelopathy. Rajan PV 외. _Clinical spine surgery_. 2022-12-01. [문헌 고찰] [DOI 10.1097/BSD.0000000000001408](https://doi.org/10.1097/BSD.0000000000001408) [PMID 36447347](https://pubmed.ncbi.nlm.nih.gov/36447347/) — 퇴행성 경추 척수병증 영상기법 개관, 단순촬영의 위치를 정리.
[^89]: Artificial Intelligence and Deep Learning for Rheumatologists. McMaster C 외. _Arthritis & rheumatology_. 2022-12. [문헌 고찰] [DOI 10.1002/art.42296](https://doi.org/10.1002/art.42296) [PMID 35857865](https://pubmed.ncbi.nlm.nih.gov/35857865/) — 류마티스 영역 AI·딥러닝 적용의 임상 통합·해석가능성 논의.
[^90]: Incorporating Artificial Intelligence into Fracture Risk Assessment: Using Clinical Imaging to Predict the Unpredictable. Kong SH. _Endocrinology and metabolism (Seoul, Korea)_. 2025-08. [문헌 고찰] [DOI 10.3803/EnM.2025.2518](https://doi.org/10.3803/EnM.2025.2518) [PMID 40754720](https://pubmed.ncbi.nlm.nih.gov/40754720/) — 임상영상을 이용한 골절위험 AI 예측의 가능성과 한계 논의.
[^91]: Diagnostic radiology—patient dosimetry. Colin J Martin 외. _Oxford Medicine Online_. 2015-01. [문헌 고찰] [DOI 10.1093/med/9780199655212.003.0014](https://doi.org/10.1093/med/9780199655212.003.0014) — X-ray 환자 선량학의 원리와 ALARA 원칙 정리.
[^92]: Diagnostic radiology equipment. Jerry R Williams. _Oxford Medicine Online_. 2015-01. [문헌 고찰] [DOI 10.1093/med/9780199655212.003.0012](https://doi.org/10.1093/med/9780199655212.003.0012) — X-ray 장비 구성요소와 화질·선량 관계 정리.
[^94]: Clinical presentation and imaging of bone and soft-tissue sarcomas. Ilaslan H 외. _Cleveland Clinic journal of medicine_. 2010-03. [문헌 고찰] [DOI 10.3949/ccjm.77.s1.01](https://doi.org/10.3949/ccjm.77.s1.01) [PMID 20179183](https://pubmed.ncbi.nlm.nih.gov/20179183/) — 골·연부조직 종양의 단순촬영 소견과 감별진단 개관.
[^97]: Color Doppler Sonography Accompanied by Dynamic Scanning for the Diagnosis of Ankle and Foot Fractures. Oh MJ 외. _Journal of ultrasound in medicine_. 2018-06. [증례 보고] [DOI 10.1002/jum.14488](https://doi.org/10.1002/jum.14488) [PMID 29159856](https://pubmed.ncbi.nlm.nih.gov/29159856/) — 발목·발 골절 평가에서 동적 초음파 병행 활용 증례.
[^100]: Scalable and Robust Artificial Intelligence for Spine Alignment Assessment: Multicenter Study Enabling Automated Measurement of Spinal Parameters from Whole-Spine Radiographs. Kim H 외. _Radiology. Artificial intelligence_. 2024-05. [실험연구] [DOI 10.1148/ryai.230094](https://doi.org/10.1148/ryai.230094) [PMID 38446041](https://pubmed.ncbi.nlm.nih.gov/38446041/) — 전신 척추 X-ray에서 정렬 지표를 자동 측정하는 다기관 AI 검증 근거.
[^101]: Multi-parameter scoliosis evaluation from dual-view x-rays via a local sine-based projection model. Wang X 외. _Physics in medicine and biology_. 2026-08-03. [실험연구] [DOI 10.1088/1361-6560/ae8ca3](https://doi.org/10.1088/1361-6560/ae8ca3) [PMID 42468563](https://pubmed.ncbi.nlm.nih.gov/42468563/) — 다시점 X-ray 기반 척추측만증 다변수 자동평가(Cobb각·관상면 균형) 딥러닝 근거.
[^104]: Dual energy X-ray absorptiometry measurements in small subjects: conditions affecting clinical measurements. Koo WW 외. _Journal of the American College of Nutrition_. 2004-06. [실험연구] [DOI 10.1080/07315724.2004.10719363](https://doi.org/10.1080/07315724.2004.10719363) [PMID 15190045](https://pubmed.ncbi.nlm.nih.gov/15190045/) — 체구가 작은 피검자(소아 등)에서 DXA 측정 조건의 영향 근거.
[^108]: Accurate automated 3D lumbar spine reconstruction from biplanar X-rays using multi-task deep learning. Yu W 외. _Medical physics_. 2026-08. [실험연구] [DOI 10.1002/mp.70570](https://doi.org/10.1002/mp.70570) [PMID 42482570](https://pubmed.ncbi.nlm.nih.gov/42482570/) — 이면상 X-ray로부터 요추 3차원 재구성을 수행하는 딥러닝 근거.
[^109]: Artificial intelligence X-ray measurement technology of anatomical parameters related to lumbosacral stability. Zhou S 외. _European journal of radiology_. 2022-01. [실험연구] [DOI 10.1016/j.ejrad.2021.110071](https://doi.org/10.1016/j.ejrad.2021.110071) [PMID 34864427](https://pubmed.ncbi.nlm.nih.gov/34864427/) — 요추-천골 이행부 해부학적 지표의 AI 자동측정 근거.
[^112]: Enhancing X-ray-Based Wrist Fracture Diagnosis Using HyperColumn-Convolutional Block Attention Module. Oh J 외. _Diagnostics_. 2023-09-13. [실험연구] [DOI 10.3390/diagnostics13182927](https://doi.org/10.3390/diagnostics13182927) [PMID 37761294](https://pubmed.ncbi.nlm.nih.gov/37761294/) — 손목 골절 X-ray 진단에서 주의집중 메커니즘 적용 딥러닝 근거.
[^114]: Improving osteoporotic vertebral deformity detection on chest frontal view radiograph by adjusted X-ray beam. Du EZ 외. _Journal of orthopaedic translation_. 2021-05. [실험연구] [DOI 10.1016/j.jot.2021.04.001](https://doi.org/10.1016/j.jot.2021.04.001) [PMID 34036040](https://pubmed.ncbi.nlm.nih.gov/34036040/) — 흉부 정면상에서 척추 압박변형 검출력을 높이는 X선 빔 조정 기법 근거.
[^116]: A software program for automated compressive vertebral fracture detection on elderly women's lateral chest radiograph. Xiao BH 외. _Quantitative imaging in medicine and surgery_. 2022-08. [실험연구] [DOI 10.21037/qims-22-433](https://doi.org/10.21037/qims-22-433) [PMID 35919046](https://pubmed.ncbi.nlm.nih.gov/35919046/) — 흉부 측면상에서 척추압박골절 자동검출 소프트웨어 근거.
[^117]: Automatic AI tool for opportunistic screening of vertebral compression fractures on chest frontal radiographs. Qiu Q 외. _Bone_. 2025-02. [실험연구] [DOI 10.1016/j.bone.2024.117330](https://doi.org/10.1016/j.bone.2024.117330) [PMID 39549901](https://pubmed.ncbi.nlm.nih.gov/39549901/) — 흉부 정면상에서 척추압박골절을 기회적으로 선별하는 AI 도구 근거.
[^119]: Calculation of the cardiothoracic ratio from portable anteroposterior chest radiography. Chon SB 외. _Journal of Korean medical science_. 2011-11. [실험연구] [DOI 10.3346/jkms.2011.26.11.1446](https://doi.org/10.3346/jkms.2011.26.11.1446) [PMID 22065900](https://pubmed.ncbi.nlm.nih.gov/22065900/) — 휴대용 전후방 촬영에서 심흉비 산출법의 표준 후전방 촬영과의 차이 보정 근거.
