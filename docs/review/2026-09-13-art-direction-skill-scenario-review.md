# Art-direction skill: prior art, scenario span, and multi-stage review

> **상태:** 결정 프로브 해소 완료, 설계 검토 리포트. 구현 전 인간 검토 대상.
> **작성일:** 2026-09-13
> **범위:** 게임 에셋(래스터 스프라이트·런타임 스크린샷·SVG) 1차 아트 디렉팅을 루틴화하는 스킬/MCP의 설계 검토. 3D 렌더·텍스처·머티리얼은 제외.
> **동반 문서:** [`ART_DIRECTION_SKILL_PLAYBOOK.md`](../../ART_DIRECTION_SKILL_PLAYBOOK.md) — 실행 절차.
> **입력 고정:** `ad_ta_vocab/ad_ta_manipulative_vocab.v1.json` SHA-256 `6e0663094024bdc7f5799932780e4d440f1d8c7ffc7e837c6f9fe0567aa58c71` (492 entries, 22 categories), `ad_ta_instruction.v1.schema.json` SHA-256 `e2b91fb292d0a75982a98fc72d0e75e250240e83ef7cdcca01f941ac4a01a044`. 참고 스펙: `hq-gamedev/docs/superpowers/specs/2026-08-27-typed-visual-art-direction-system-design.md`, `hq-gamedev/docs/reviews/2026-08-27-taste-skill-source-backed-adoption-review.md`.
> **확신 표기:** `[확실함]` 직접 확인, `[추정]` 근거 있는 추론, `[확인 안 됨]` 미검증.

## 1. 결론

**GPU 없음, 캘리브레이션 사례 0건, 팀 무관(agnostic) 배포라는 세 제약 아래에서 지연된 실패가 통제되는 경로는 하나다. 관찰 레코드를 정본으로 두고 이미지 벡터를 재구축 가능한 캐시로만 얹는 하이브리드(S3)를, 스킬+스크립트로 시작해 동일 파이썬 코어 위에 MCP 전송층만 추가하는 방식으로 승격하는 것이다.**

이 결론을 지지하는 근거는 세 묶음이다.

1. **선행 사례에는 판단 루틴이 비어 있다.** 팔레트 추출, 픽셀아트 생성, ImageMagick/Inkscape/Blender MCP, 리터칭 에이전트 논문까지 부품은 전부 존재하지만, "AD가 스크린샷을 보고 vibrance를 5% 올리자고 판단하는 과정"을 코퍼스와 선례로 루틴화한 완성 스킬은 없다. 재발명이 아니라 조립이다. (3절)
2. **비용과 실패 분석이 S3를 고른다.** 관찰 레코드는 stdlib만으로 굴러가고(SQLite조차 불필요), 이미지 벡터는 "지워도 시스템이 동작하는 캐시"라는 불변식을 지킬 때만 걱정이 없다. 학습은 canonical 승격 시에만 일어나며 append-only라 destructive learning이 없다. (5절)
3. **`ad_ta_vocab`는 이미 조작 표면을 갖고 있다.** 492개 표제어 중 291개가 2D 범위 규칙을 통과하고, 12개 연산 레지스트리와 quantification mode가 "지각 목표 ≠ 수치 노브"를 구조적으로 분리한다. 교육 맥락과 한국어 전용 필드를 걷어내면 stock 층의 어휘로 바로 쓸 수 있다. 다만 어휘만 있고 사례가 없으므로 stock 사례 40건은 별도로 저작해야 한다. (7절)

가장 큰 열린 위험은 롤백이 아니라 **선례 오염**과 **VLM의 색 정량 불능**이다. 앞의 것은 canonical 전용 검색과 승격 시 충돌 검사로, 뒤의 것은 "방향은 모델, 크기는 측정과 선례"라는 분업으로 막는다. (10절, 11절)

## 2. 결정 프로브 해소

| ID | 질문 | 해소 | 설계에 미친 결과 |
|---|---|---|---|
| P1 | 코퍼스 저장 단위 | 하이브리드, 관찰 레코드 우선 `[확실함]` | 정본은 JSONL 관찰 레코드. 이미지 벡터는 `(model_id, sha256)` 키의 재구축 캐시. SQLite 불필요. 5.1절 |
| P2 | 임베딩 위치·egress | 기본 API on, 팀별 off 가능 `[확실함]` | OpenRouter 크레딧으로 `voyageai/voyage-multimodal-3.5` 사용 가능. Cohere Embed v4는 OpenRouter에 없음. off 시 기능 축소표 5.2절 |
| P3 | 자동화 상한·학습 | 미리보기+승인, 분리 출력 경로, canonical 승격 시에만 학습 `[확실함]` | 원본 불변, 롤백 축 제거. 학습은 레코드 승격이며 가중치 변경 없음. 5.3절 |
| P4 | 코퍼스 씨앗 | `ad_ta_vocab` 정제본 + 공개 가독성 휴리스틱 + taste-skill adopt/adapt `[확실함]` | stock 층 = 어휘(정제) + 사례(저작). team 층은 빈 채로 출발. 7절 |
| P5 | 1차 입력 | 래스터 PNG, 런타임 스크린샷, SVG `[확실함]` | 3D 제외로 tool 유닛은 ImageMagick·Inkscape·Pillow로 닫힘. 9.4절 |
| P6 | hq-gamedev 결합도 | 독립, provenance 무관 `[확실함]` | 레코드에 내부 해시·supersedes만 둠. 외부 API·계약·CAS 없음. 6절 |
| P7 | 패키징 | 스킬 → MCP 승격, 스펙 무손실 `[확실함]` | 단일 파이썬 코어, CLI와 MCP는 전송층. conformance fixture 공유. 9.5절 |
| P8 | 캘리브레이션 쌍 | 0건 `[확실함]` | greenfield 기본. 취향 부트스트랩은 pairwise 선호 질문. vision 유닛은 단계적. 9.3절 |
| P9 | 문서 위치 | 관례대로 `[확실함]` | 리포트 `docs/reviews/`, 플레이북 레포 루트 |

## 3. 선행 사례 조사

### 3.1 같은 컨셉의 완성 스킬은 없다

`[확실함]` 2026-09-13 기준 웹·마켓·사내·형제 레포 조사에서 "인간 AD/TA의 판단 기준을 코퍼스와 선례로 루틴화하고, 그 판단을 결정적 툴 조작으로 연결하는" 완성 스킬이나 MCP는 발견되지 않았다. 존재하는 것은 아래처럼 부품이다.

### 3.2 인접 사례와 성공·pain point

| 사례 | 하는 일 | 성공한 것 | pain point | 우리가 가져올 것 |
|---|---|---|---|---|
| `Leonxlnx/taste-skill` (사내 리뷰 완료, adopt 3/adapt 7/reject 5) | 웹 프론트 취향 스킬 | brief 구조화(M04), Preserve/Overhaul(M02), 레퍼런스의 quality/rhythm 분석(M01), 구조화 관찰(M03), pre-flight(M08) | 웹 취향의 보편 금지 승격(M13), 생성 필수(M11), 사실 발명(M12), provenance·evidence·rights 토큰 0건(M15) | M01·M02·M03·M08의 절차 골격만. 게임 그래픽 언어와 부정합이므로 어휘는 가져오지 않음 |
| `agent-sprite-forge` (형제 레포, Codex 스킬) | 2D 스프라이트 생성+결정적 후처리 | "에이전트가 계획, 스크립트는 판단하지 않고 처리만" 패턴. 액션 간 scale profile 잠금. anchor sheet. QC 메타데이터 | 미적 판단 없음. 기하 QC만. 생성 우선이라 기존 에셋 디렉팅에는 부적합. 단일 행 시트 드리프트, video2dsprite identity drift를 스스로 경고 | tool 유닛의 계약("스크립트는 창작 판단 금지"), scale profile을 group cohesion lock의 선례로 |
| Claude 스킬 마켓 (pixel-art-professional, color-palette-extractor, ImageSearch, claude-art-skill) | 팔레트 k-means+WCAG, 픽셀아트 생성, 브랜드 미학 md 파일 | 브랜드 미학을 md 파일 하나로 두는 zero-DB 접근 | 코퍼스·선례·판단 루틴 없음. 생성 편향 | S0(md 파일) 시나리오의 선례. greenfield 모드가 여기서 출발 |
| ImageMagick MCP(57툴), Inkscape MCP(60+), Blender MCP(218), DCC-MCP | 툴 노출 | 툴 유닛 자체는 재발명 불필요. DCC-MCP의 "vision은 해석, 결정적 측정이 진실층" 원칙 | 툴 수가 곧 컨텍스트 토큰. 판단 없이 툴만 있음 | 동사 8개 이하의 얇은 helper. 이미지 대신 JSON 통계를 반환해 토큰 절감 |
| PhotoAgent, PerTouch, RefineEdit-Agent, TalkPhoto (2025-2026 논문) | VLM 리터칭 에이전트 | perceiver→planner→executor→evaluator 폐루프. VLM이 리터칭 툴을 호출 | 단일 사진 미학. 팀 취향·선례·게임 가독성 없음. MCTS 등 무거운 탐색 | 루프 구조. 특히 "evaluator가 executor와 분리" |
| VILA, Q-Align, UNIAA, UniQA | 미학 스코어러 | 제로샷 미학 점수 | GPU 파인튜닝 필요, 절대 점수, 게임 도메인 아님 | 제외. 절대 점수 자체를 설계에서 배제하는 근거로만 사용 |
| LAION aesthetic predictor 계열 | CLIP 임베딩 위 선형 head | "naive embedding + 작은 head"가 통한다는 선례 | 사진 미학 편향 | 이미지 벡터를 캐시로 두는 S3의 정당화 |
| SigLIP 2, JinaCLIP v2, voyage-multimodal-3.5, Gemini Embedding 2, Nemotron Embed VL | 이미지 임베딩 | 오픈 가중치(SigLIP2)와 API(Voyage) 둘 다 존재. OpenRouter 단일 크레딧 | CPU 실행은 저볼륨에서만 현실적. 모델 교체 시 전량 재임베딩 | P2 기본값의 근거 |

### 3.3 설계를 구속하는 pain point 증거

- **VLM은 색을 정량하지 못한다.** `[확실함]` ColorBench와 색맹검사 연구에서 LVLM은 near-random 수준이고, saturation 대비에는 민감하지만 brightness 대비에는 둔하며 red 편향이 있다. 색 이름도 거친 범주로 뭉갠다. 결론: "vibrance +5%"의 **크기**를 VLM이 정하게 하면 안 된다. 방향("칙칙하다")만 VLM, 크기는 결정적 측정과 승인 선례.
- **MLLM-as-judge는 불안정하다.** `[확실함]` position bias로 최대 40% 비일관, 숫자 스코어는 불안정, pairwise 비교가 반복 가능하다는 보고가 다수다. 결론: 절대 점수 대신 "선례 대비 pairwise"와 "qualified level(asserted/estimated/unknown)".
- **인디 팀의 1위 pain은 포즈·에셋 간 일관성이다.** `[확실함]` 생성 툴 벤더와 r/gamedev 스레드가 공통으로 말한다. "AI는 고립된 완성도는 내지만 게임의 응집은 못 낸다", "미세 조정하려 들수록 나빠진다". 결론: 단일 이미지 미학보다 group cohesion과 intentional contrast 축이 먼저다.
- **툴 수는 토큰이다.** `[추정]` 57~218개 툴을 가진 MCP는 스키마만으로 컨텍스트를 잠식한다. 얇은 동사 집합이 목표에 맞는다.
- **아트 파이프라인 없는 스타일 정의는 실패한다.** `[확실함]` r/gamedev의 AD 발언: "팀들이 제대로 된 아트 파이프라인 없이 비주얼 스타일을 세우려다 이 문제에 부딪힌다". 결론: 이 스킬은 스타일을 만들어주는 도구가 아니라 파이프라인의 판단 단계를 기록·재사용하는 도구여야 한다.

## 4. 시나리오 스팬과 선택

| | 코퍼스 형태 | 비전 유닛 | tool 유닛 | 지연 실패의 주된 형태 | 판정 |
|---|---|---|---|---|---|
| S0 메모 파일 | 규칙·사례 md 1개 | Claude 비전 판단만 | ImageMagick 레시피 | 사례 20건 넘으면 컨텍스트 붕괴, 선례 검색 불가 | greenfield 모드로 흡수 |
| S1 관찰 레코드 | 결정적 측정+구조화 관찰 JSONL, 어휘 ID·특징 벡터 k-NN | 관찰→선례 매칭 | 동일 | "닮은 그림"을 못 찾음(어휘·통계만) | S3의 정본층 |
| S2 이미지 벡터 | CLIP/SigLIP 벡터 인덱스 | 유사 이미지 선례 | 동일 | 벡터가 불투명·비diff, 모델 교체 시 전량 재임베딩, API 의존 | 단독으로는 거부 |
| S3 하이브리드 | S1 정본 + S2 캐시 | 둘 다, 캐시 부재 시 S1로 degrade | 동일 | S1과 같음 + 캐시 관리 | **선택** |
| S4 typed-visual 통합 | provenance API 12타입 | Midori 계약 | recipe registry | 팀 무관 배포 불가, 0건 캘리브레이션에서 threshold 정책 정의 불가 | 참조만 |

S0와 S4는 양 끝의 북엔드다. S0는 team 층이 비어 있는 greenfield 상태 그 자체이고, S4는 세 축 분리·evidence region·alpha 불변 같은 불변식을 빌려오는 출처다.

## 5. 세 질문에 대한 답

### 5.1 P1: 관찰 레코드 vs 이미지 벡터의 엔드유저 실패 비용

관찰 레코드에 SQLite는 필요 없다. 소규모 팀의 코퍼스는 수백에서 수천 건이고, 어휘 ID 희소 벡터와 정규화 측정치를 이어 붙인 벡터의 cosine 전수 스캔은 밀리초다. 파일은 JSONL append-only이며 git diff로 읽힌다.

| 저장 방식 | 설치 의존 | 런타임 의존 | 대표 실패 모드 | 엔드유저 실패 비용 | diff 가능 | 재구축 가능 |
|---|---|---|---|---|---|---|
| JSONL + 희소 어휘/특징 벡터 (선택) | 없음 (stdlib) | 없음 | 크래시 시 마지막 줄 절단 | 거의 0. write-then-rename으로 절단 방지. 동시 쓰기는 파일 잠금 한 줄 | 예 | 정본 자체 |
| SQLite | 없음 (stdlib) | 없음 | 동시 writer 잠금, 스키마 마이그레이션, WAL 파일 잔존 | 낮음. 그러나 diff 불가, 마이그레이션 관리가 생김 | 아니오 | 정본이면 백업 필요 |
| 텍스트 임베딩(자유 코멘트용, 선택적) | API 키 또는 로컬 모델 | 네트워크 | 모델 교체 시 벡터 불일치 | 중간. 다만 어휘 ID 매핑이 1차이고 텍스트 벡터는 보조라 off 가능 | 아니오 | 예 (원문 보존) |
| 이미지 벡터, 로컬 오픈 모델 | torch+가중치 (GB 단위) | CPU 초 단위/이미지 | 설치 실패, 버전 드리프트, 메모리 | 높음. 설치가 곧 지원 티켓 | 아니오 | 예 (원본 이미지 보존) |
| 이미지 벡터, API | API 키 | 네트워크, 과금, egress 정책 | 모델 버전 교체(3→3.5) 시 의미 드리프트, rate limit, 오프라인 | 중간. 캐시로만 쓰면 낮음 | 아니오 | 예 |

판정 `[확실함]`: 관찰 레코드는 걱정이 없다. 이미지 벡터는 다음 불변식을 지킬 때만 걱정이 없다.

- 벡터는 `(model_id, content_sha256)`를 키로 하는 파생 캐시이며 정본이 아니다.
- 캐시 디렉터리를 통째로 지워도 모든 테스트가 통과하고, 사라지는 것은 "시각적으로 닮은 선례" 제안 하나뿐이다.
- 모델을 바꾸면 캐시는 자동 무효화되고 백그라운드로 재구축된다. 두 모델의 벡터를 한 인덱스에 섞지 않는다.

이 불변식이 conformance test로 존재하면 하이브리드로 가도 된다. 존재하지 않으면 S1로 시작하는 것이 옳다.

### 5.2 P2: API on/off 기능 차이

에셋 바이트가 기계 밖으로 나가는 경로는 두 개다. Claude 비전(Anthropic)은 스킬이 Claude Code 안에서 돌기 때문에 본질적이고, 임베딩 API는 선택적이다. "외부로 안 읽힘"을 완전히 만족하려면 로컬 VLM이 필요한데 GPU 없는 팀에는 범위 밖이므로 정직하게 표기한다.

| 기능 | 오프라인(stdlib+ImageMagick) | Claude 비전만 | Claude 비전 + 임베딩 API |
|---|---|---|---|
| 결정적 측정(팔레트, 휘도·채도 히스토그램, 대비, 알파 점유, 실루엣 마스크, 엣지 밀도, 다중 배율) | 가능 | 가능 | 가능 |
| 레시피 미리보기·적용·diff | 가능 | 가능 | 가능 |
| 어휘 ID·측정치 기반 선례 검색 | 가능 | 가능 | 가능 |
| 질적 관찰(26개 perceptual goal, evidence region) | 불가 | 가능 | 가능 |
| 방향 제안·pairwise 비교·ingest 서술 매핑 | 불가 | 가능 | 가능 |
| "시각적으로 닮은 승인 선례" 검색 | 불가 | 불가 | 가능 |
| 자유 코멘트의 벡터 검색 | 불가 | 어휘 ID 매핑으로 대체 | 가능 |
| 외부로 나가는 바이트 | 없음 | 이미지 → Anthropic | 이미지 → Anthropic + 임베딩 제공자 |

기본값은 마지막 열이며, `embedding.enabled=false` 한 줄로 셋째 열로 떨어진다. 첫째 열은 CI와 배치 측정용이다. zero-retention은 API 계약상 국룰에 가깝지만 `[확인 안 됨]` OpenRouter 경유 시 각 제공자의 데이터 정책 전파는 팀이 직접 확인해야 한다. 플레이북에 확인 항목으로 둔다.

### 5.3 P3: canonical 승격 시에만 학습, destructive learning 없음

이 시스템에는 가중치가 없다. "모델"은 레코드 집합 위의 k-NN이므로 학습은 곧 레코드 승격이다.

- 계층: `stock`(패키지 동봉, 버전 고정) < `team/canonical`(검색 대상) < `team/candidate`(저장만, 검색 제외). 검색은 canonical과 stock만 본다.
- 학습 = candidate → canonical 승격. 인간 승인이 유일한 트리거다. 사용자의 제안대로 "canonical 승격 시에만" 학습한다.
- 롤백 = 레코드에 `superseded_by`를 붙이고 인덱스를 재구축한다. 삭제는 없다. 인덱스는 파생물이므로 재구축은 결정적이다.
- 충돌 검사 = 승격 시 같은 `(context, facet)`에서 반대 stance의 canonical이 있으면 승격을 막고 두 레코드를 나란히 보여 준다. 이것이 첨부 스펙의 `TASTE_CONFLICT_UNRESOLVED`를 한 줄로 줄인 것이다.
- 코퍼스 임베딩 롤백 = 벡터는 캐시이므로 롤백 개념이 없다. 레코드 상태가 바뀌면 인덱스에서 빠질 뿐이다.

따라서 destructive learning은 구조적으로 불가능하다. 유일한 파괴 경로는 레코드 병합·요약 같은 손실 변환인데, 이를 금지 항목으로 둔다.

## 6. 첨부 스펙(typed visual art-direction)의 비판적 참조

첨부 스펙은 S4다. 팀 무관 배포와 0건 캘리브레이션이라는 조건에서 그대로 쓸 수 없지만, 불변식의 상당수는 소규모 팀에도 그대로 유효하다.

### 6.1 가져오는 것

| 스펙 항목 | 가져오는 형태 | 이유 |
|---|---|---|
| 세 평가축 분리 (`direction_compliance` / `asset_cohesion` / `intentional_contrast`) | JudgmentRecord의 `axis` 필드. 하나의 taste score로 평균하지 않음 | 인디 pain 1위가 cohesion이고, 의도적 대비 오독이 지연 실패 2순위 |
| `EvidenceRegion` (whole_image / bbox) | ObservationRecord의 `regions` | 게슈탈트 대응. 격자 대신 모델·마스크가 고른 영역 |
| `asserted / estimated / unknown` qualified level | 모든 관찰·판단 필드 | VLM 불안정성을 레코드에 흡수 |
| RGB-only color grade, decoded alpha plane pre/post hash 동일 | tool 유닛 불변식 | 스프라이트의 alpha는 게임플레이 마스크다. 건드리면 콜리전·정렬이 깨진다 |
| recipe identity = ops+params+tool version의 canonical hash | RecipeRun manifest | 재현성. 같은 입력·레시피·툴이면 같은 출력 해시 |
| source ≠ runtime, 원본 불변, derived는 새 경로 | 사용자가 이미 결정한 분리 출력 경로 | 롤백 축 제거 |
| `unmapped`는 LLM 추측으로 채우지 않음 | 완화: LLM 매핑 허용하되 `mapped_by=llm`으로 표기, canonical 승격 시 인간 확인 | 팀 무관 배포에서 인간 승인 alias 테이블만으로는 콜드 스타트 불가 |
| candidate vs approved 분리, supersede 기반 immutable revision | 3계층 코퍼스 | 선례 오염 차단 |
| narration과 evaluation의 2단 분리 (6.6a / 6.6b) | vision 유닛의 observe → judge 분리 | 관찰이 판단에 오염되지 않게. pairwise judge 입력을 관찰 레코드로 고정 |
| vibrance는 algorithm revision 없이 수치화 금지 | 레시피 카탈로그에 알고리즘 명시 | ImageMagick에 vibrance 원어가 없으므로 정의 필수 |
| 읽기 집합 고정(read-set hash) | JudgmentRecord의 `context_hash` (stock 버전 + canonical 인덱스 해시 + 측정치) | 같은 판단을 재현·감사 |

### 6.2 버리는 것

| 스펙 항목 | 버리는 이유 |
|---|---|
| provenance API, K0 store, CAS head, lineage readback | P6. 팀 무관 배포. 내부 해시와 `supersedes`로 충분 |
| 12개 strict Pydantic domain type, JSON-LD 위장 금지 규칙, 16MB cap | 배포 대상이 1인 팀부터라 계약 표면이 곧 진입 장벽. 레코드 4종으로 축소 |
| Discord `TrustedHumanApprovalOrigin`, one-hop contract, Midori 정체성 검증 | 팀 고유 운영 체계 |
| `TasteStabilityPolicyRevision`의 정수·basis point threshold | 0건 캘리브레이션에서 정의 불가. 계층+건수+충돌 검사로 대체 |
| `ArtLanguageMapRevision`의 인간 승인 전용 alias 개정 | git에서 편집하는 alias 파일 + 승격 시 확인으로 대체 |
| 골든 배치 2/2/2, Unity Development Player, G1/G2/G4 | 특정 프로젝트 조건. 대신 conformance fixture 6장(래스터 2, 스크린샷 2, SVG 2) |
| 자동 `integration-ready` 승격 | 미리보기+승인이 상한. 그 위는 team 층이 생긴 뒤의 옵션 |

### 6.3 스펙이 가르쳐 준 것 중 이 설계가 다르게 답하는 지점

스펙은 LLM의 언어 이해를 mapping evidence로 인정하지 않는다. 팀 무관 배포에서는 그 원칙을 지키면 첫 사용자가 alias 테이블부터 손으로 써야 한다. 이 설계는 LLM 제안 매핑을 허용하되 세 겹으로 격리한다. `mapped_by` 필드, candidate 계층 격리, canonical 승격 시 원문 span과 나란히 보여 주는 확인 화면. 스펙의 우려(추측이 정본이 됨)는 세 번째 겹에서 막힌다.

## 7. 코퍼스 분석: `ad_ta_vocab` → stock 층

### 7.1 무엇이 있는가 `[확실함]`

- 492 entries, 22 categories, 30 tools, 8 sources. 언어 `ko-KR`. 항목마다 `id`, `category`, `label_en`, `label_ko`, `search_terms`, `kind`(11종), `description_ko`, `provenance.evidence`(대화 인용 오프셋), `operationalization`(candidate_surfaces 50종, guidance_ko, perceptual_review_required), `quantification`(profile 50종, mode 8종, allowed_units 35종, required_context, allowed_operations), `curriculum_weeks`, `confusable_with`, `verified_doc_ids`.
- 정말 쓸 만한 구조 세 가지. 첫째, `quantification.mode`가 `proxy_only | qualitative | relational | structural | categorical | measurable_with_context | direct_with_context`로 나뉘어 "지각 목표에는 수치 노브가 없다"를 스키마가 강제한다. 둘째, `operation_registry` 12종이 `set / add_delta / multiply / relative_delta / percentage_point_delta / set_relation / set_sequence / define_metric / measure / propose_variation / compare / describe`로 조작 의미를 고정하고 `baseline_required`를 명시한다. 셋째, `numeric_rules`의 `baseline_percent`, `named_grid`, `proxy_not_truth`, `thresholds_not_norms`, `runtime_gate`가 이 스킬의 불변식과 거의 일치한다.
- `ad_ta_instruction.v1.schema.json`은 "의도 → 어휘 ID → 대상/연산 → 단위/맥락 → 런타임 바인딩/승인 → 측정 증거" 흐름의 요청 데이터다. vision 유닛이 내는 방향 제안의 직렬화 형식으로 그대로 확장 가능하다.
- `validate_export.py`의 `lint_instruction`은 이미 "proxy_only 항목에 set/relative_delta 금지", "delta 연산에 baseline_ref 필수", "define_metric에 metric 정의 필수"를 검사한다. tool 유닛의 pre-flight로 재사용한다.
- `vocab_cli.py`는 stdlib만으로 `search/get/category/lint`를 제공한다. README가 이미 "전체 사전을 LLM에 주입하지 말고 검색 → ID 조회"를 지시한다. 이 원칙을 스킬에 그대로 계승한다.

### 7.2 걷어내고 바꾸는 것 (사용자 지시 + 이 검토의 추가 배제)

| v1 필드 | v2 처리 | 근거 |
|---|---|---|
| `language: ko-KR` | `language: en` + 선택적 `i18n` 맵 | 표준은 영어. 모든 언어 대응 |
| `label_ko`, `categories[].label_ko` | `label`(영어) + `i18n.ko.label` 선택 | 사용자 지시 |
| `description_ko`, `guidance_ko`, `confusable_with[].note_ko`, `quantification.note`, `numeric_rules[].rule_ko`, `ambiguous_tokens[].resolution_note_ko` | 영어 업계 표준 어휘로 치환한 `description`, `guidance`, `note`, `rule` | 사용자 지시 |
| `search_terms` | `aliases: [{text, lang}]`. 한국어 별칭은 검색용으로 보존 | 아티스트가 한국어로 입력하는 경로는 유지해야 ingest가 된다. 교육 맥락이 아님 |
| `curriculum_weeks` (entries, categories) | 삭제 | 사용자 지시 |
| `provenance.evidence`, `sources`, `coverage_audit` | 삭제. `origin: "ad_ta_vocab.v1"`와 원본 항목 해시만 남김 | 인터뷰·13주 커리큘럼 대화 인용은 교육 맥락. 의심 필드 |
| `tools` (30개, 대화 역할 기록) | 삭제. tool 유닛의 자체 registry(imagemagick, inkscape, pillow)로 대체 | `binding_state: unbound`, `availability: not_checked`인 목록은 실행 근거가 아님 |
| `technical_verification_sources`, `runtime_binding_examples`, `verified_doc_ids` | 삭제. 필요 시 `references` 선택 필드로 재도입 | Unity FOV·URP Lit·Blender 바인딩은 3D·엔진 범위 |
| `extraction_contract`, `metadata`, `known_limits` | v2 계약으로 재작성 | 원문은 추출 작업의 계약이지 배포물의 계약이 아님 |
| `operationalization.binding_state`, `is_executable_command` (const) | 삭제 | 상수 노이즈. 실행 게이트는 InstructionRecord의 `execution` 블록이 담당 |
| `methods` 카테고리 20개, `local_meta` 2개 | 삭제 | 학습 방법론과 대화 로컬 메타어휘 |
| `material`, `geometry`, `uv_texture`, `rig_animation`, `shader`, `render` 카테고리 | 삭제 | P5 범위 밖 |
| `intent_ko`, `note_ko`, `description_ko`, `definition_ko` (instruction schema) | `intent`, `note`, `description`, `definition` | 사용자 지시 |
| instruction `status: design_only`, `execution.*: false` (const) | `status: proposed\|previewed\|approved\|applied\|rejected\|superseded`, `execution` 실필드 | 실제 실행 상태를 기록해야 학습이 됨 |

### 7.3 범위 필터 결과 `[확실함]`

규칙: 위 카테고리 삭제 후, `candidate_surfaces`가 2D 표면 집합 `{screen_layout, perceptual_evaluation, image_regions, color_values, palette, color_pipeline, vector_paths, vector_document, sprite_import, sprite_renderer, image_grid, timeline, animation_curve, measurement, asset_constraints, render_capture, asset_manifest, export_configuration, reference, comparison_record, viewport, coordinate_conversion}`와 교차하는 항목만 유지.

| 결과 | 수 |
|---|---:|
| 원본 | 492 |
| 카테고리 삭제 | 159 |
| 표면 불일치 삭제 | 42 |
| 규칙 통과 | 291 |
| 수동 재편입 (painted lighting: `light_direction`, `form_shadow`, `cast_shadow`, `terminator`, `backlight`, `fake_lighting`; 2D VFX sheet: `flipbook`, `frame_strip`, `birth`, `expansion`, `impact`, `breakup`, `dissipation`, `trailing_motion`) | 약 14 |
| stock 어휘 v2 예상 | 약 305 |

규칙 통과 291의 분포: perception 23, composition 26, shape 40, space 21, camera 16, value 10, color 25, vector 22, pixel_sprite 23, motion 43, qc 21, pipeline 21. kind별로는 perceptual_goal 26, principle 12, diagnostic 13, visual_structure 56, operation 30, parameter 45, representation 88, constraint 14, pipeline 7. `perceptual_review_required`가 105건이다.

두 어휘 집합이 vision 유닛과 tool 유닛을 각각 규정한다.

- **판단 어휘** = perceptual_goal 26 + principle 12 + diagnostic 13. 예: `perception.silhouette_readability`, `perception.figure_ground`, `perception.visual_hierarchy`, `perception.style_coherence`, `perception.visual_clutter`, `perception.affordance`, `composition.balance`, `shape.contour_economy`, `color.perceived_color`, `color.simultaneous_contrast`, `qc.visual_regression`, `pipeline.vision_critique`, `methods.screenshot_audit`(methods지만 재편입 검토). 이들은 전부 `proxy_only` 또는 `qualitative`이므로 VLM 관찰 + 대리지표 정의(`define_metric`)로만 다룬다.
- **조작 어휘** = `direct_with_context` 또는 `measurable_with_context`인 68개. 예: `color.saturation`, `color.vibrance`, `color.hue`, `color.exposure`, `color.gamma`, `color.tint`, `color.color_temperature`, `value.highlight`, `value.shadow`, `value.grayscale`, `shape.edge_control`, `shape.notch`, `shape.proportion`, `composition.negative_space`, `composition.screen_occupancy`, `pixel_sprite.pixelation`, `pixel_sprite.pixel_snapping`, `pixel_sprite.internal_resolution`, `vector.stroke`, `vector.viewbox`, `space.scale`. 이 중 래스터 툴로 직접 실행 가능한 것은 색·값·픽셀 계열 약 20개이며, 나머지는 측정(`measure`)과 제안(`propose_variation`)까지만 자동화한다.

### 7.4 빈자리: 어휘는 있고 사례가 없다

`[확실함]` v1은 사전이지 판례집이 아니다. k-NN이 돌려면 "상황 → 판단 → 조작" 삼중항이 필요하다. stock 사례는 저작해야 한다.

- 형식: `JudgmentCase = { situation(측정치 범위 + 관찰 태그 + 맥락), judgment(axis, stance, 판단 어휘 ID, qualified level), instruction(조작 어휘 ID + operation + magnitude_basis), acceptance(numeric proxy + human), overridable: true, evidence_kind: heuristic }`.
- 출처: 공개 2D 가독성 프레임워크(silhouette priority, value hierarchy, affordance denial, "color는 보조 역할", grayscale study), 사내 taste-skill 리뷰의 M01·M02·M03·M07·M09·M10 적응판, v1의 perceptual_goal 항목 자체.
- 첫 목표 40건. 예시 제목: "figure-ground 실패 시 saturation보다 value contrast 먼저", "실루엣이 64px에서 뭉개지면 tertiary detail 제거", "actionable 아닌 오브젝트의 affordance 거부(색·형태 대비 낮춤)", "같은 asset group 내 palette hierarchy 이탈 감지", "의도적 대비(진영·상태)는 cohesion 위반이 아님", "dull 판정은 saturation 분포와 value range를 함께 본다", "UI 아이콘 가독성은 stroke 폭과 negative space 비율", "픽셀 스프라이트는 pixel_snapping 후 판단", "SVG는 rasterize 배율 두 개에서 판단", "생성 원본 시트는 셀 간 scale drift 먼저".
- 규칙: 모든 수치는 `thresholds_not_norms`. 사례의 수치는 예시이며 team 층 증거가 덮어쓴다. taste-skill 리뷰의 M13(보편 금지 승격 금지)을 stock 사례 전체에 적용한다.

### 7.5 언어 정책

영어 정본. `aliases`에 언어 태그를 붙여 한국어·일본어·중국어 별칭을 보존한다. ingest 시 아티스트의 원문 span은 원어 그대로 레코드에 보존하고, 매핑된 어휘 ID만 영어다. 이는 첨부 스펙의 `NaturalLanguageSpan` 원칙을 필드 두 개로 줄인 것이다.

## 8. 게슈탈트와 이미지→코퍼스 매핑

격자로 잘라 패치를 임베딩하면 실루엣·figure-ground·위계 같은 관계가 사라진다. 파인튜닝도 그렇게 하지 않는다. 이 설계는 네 원칙으로 답한다.

1. **판단 단위는 보이는 배율의 전체 이미지다.** 에셋은 게임 내 배율로, 스크린샷은 표시 배율로. 측정과 관찰은 100%, 목표 배율, 64px 썸네일의 세 배율에서 반복한다. 실루엣 가독성은 배율 현상이라 한 배율 값은 증거가 아니다.
2. **영역은 모델이나 마스크가 고른다.** evidence region은 VLM이 관찰에 붙인 bbox 또는 결정적 분할(알파 마스크, 실루엣, saliency 근사)이 만든 영역이다. 고정 격자는 쓰지 않는다.
3. **관계를 저장한다.** 관찰 레코드는 영역 간 관계(figure/ground, hierarchy order, overlap)를 필드로 갖는다. 게슈탈트는 관계이므로 관계를 벡터화하면 검색된다.
4. **응집은 집합의 게슈탈트다.** 같은 asset group의 pairwise 거리(팔레트 EMD, value range 겹침, edge treatment 통계, 실루엣 복잡도)를 집합 단위로 계산한다. 선례 검색 키에 `asset_group`, `scene`, `state`가 들어간다.

이미지 벡터를 쓸 때도 전체 이미지와 실루엣 렌더 두 장만 임베딩한다. 패치 임베딩은 금지 항목이다. 판단은 절대 점수가 아니라 "이 관찰 레코드와 가장 가까운 canonical 선례 k개와의 pairwise"다.

## 9. 유닛 설계

### 9.1 공통 레코드 4종

| 레코드 | 내용 | 정본 위치 |
|---|---|---|
| `ObservationRecord` | `asset_sha256`, `scales[]`, `measurements{}`(팔레트, HSL 히스토그램, 휘도 분포, 대비, 알파 점유, 실루엣 지표, 엣지 밀도), `observations[]`(판단 어휘 ID, qualified level, region, note), `relations[]`, `context{asset_group, scene, state, target_scale}`, `observer{model, prompt_rev}` | `corpus/team/observations/` |
| `JudgmentCase` | 7.4의 삼중항 + `tier: stock\|candidate\|canonical`, `mapped_by`, `approved_by`, `supersedes` | `corpus/stock/cases/`, `corpus/team/{candidate,canonical}/` |
| `InstructionRecord` | `ad_ta_instruction` v2. `changes[]`에 어휘 ID·operation·quantity·`magnitude_basis`, `precedent_refs`, `status` | `runs/<id>/instruction.json` |
| `RecipeRun` | recipe hash, tool versions, input/output sha256, alpha plane pre/post hash, 통계 diff, contact sheet 경로, `status` | `runs/<id>/manifest.json` |

레코드는 JSON 한 파일 또는 JSONL 한 줄이다. 삭제 대신 `supersedes`. 인덱스(`index/*.npy`, `index/vectors/<model_id>/`)는 전부 파생물이다.

### 9.2 ingest 유닛

아티스트의 판단을 코퍼스에 녹이는 경로다.

1. 입력: 이미지(들) + 원문 코멘트("전반적으로 칙칙하니 vibrance 5% 올려 보자") + 맥락.
2. 측정: tool 유닛 `measure`로 ObservationRecord의 measurements를 채운다. 판단 당시의 수치가 없으면 나중에 선례로 쓸 수 없다.
3. 매핑 사다리: (a) `aliases` 정확 일치 → (b) 부분 일치·`ambiguous_tokens` 해소 → (c) LLM 제안(`mapped_by: llm`). 어느 단에서 매핑됐는지 기록한다. 원문 span은 그대로 보존한다.
4. 크기 해석: "5%"는 `color.vibrance relative_delta +5`이며 `baseline_ref`는 2단계 측정치다. 크기 없는 코멘트("칙칙하다")는 stance만 기록하고 magnitude는 비운다.
5. 저장: `tier: candidate`. 검색 대상이 아니다.
6. 승격: pairwise 확인 화면(원문 span, 매핑 결과, 같은 맥락의 기존 canonical, 충돌 경고)을 보고 인간이 canonical로 올린다. 이때만 인덱스가 갱신된다.

greenfield 팀의 취향 부트스트랩은 같은 경로의 특수형이다. 레퍼런스 보드나 초기 에셋 몇 장으로 "A와 B 중 어느 쪽이 우리 방향에 가깝나, 왜"를 묻고, 답을 candidate로 넣는다. pairwise는 인간 입력 형식과 모델 판단 형식을 동시에 맞춘다.

### 9.3 vision 유닛 (단계적, 사용자 지시 "천천히")

| 단계 | 하는 일 | 필요 자원 | 산출 |
|---|---|---|---|
| V0 measure | 결정적 측정만. 판단 없음 | 오프라인 | ObservationRecord.measurements |
| V1 observe | 판단 어휘 26개 중 P5 범위 항목에 대해 qualified 관찰 + evidence region. 판단·제안 금지 | Claude 비전 | ObservationRecord.observations |
| V2 retrieve+propose | canonical·stock 선례 k-NN → 세 축별 판정(pairwise) → InstructionRecord 제안. 방향은 모델, 크기는 선례·측정 | Claude 비전 | InstructionRecord(status=proposed) |
| V3 group | asset group 단위 cohesion·intentional contrast. 그룹 내 pairwise 거리 | 오프라인 측정 + Claude | axis 판정 |
| V4 visual neighbors | 이미지 벡터로 닮은 승인 선례 검색 | 임베딩 API | 선례 후보 보강 |

V1까지가 첫 구현의 상한이다. V2는 stock 사례 40건과 conformance fixture가 준비된 뒤 켠다. V2의 절대 규칙: 숫자는 `measurements`나 `precedent_refs`에서만 온다. VLM이 낸 숫자는 `magnitude_basis: llm`으로 표기되며 자동 적용 대상이 아니다.

### 9.4 tool 유닛

동사 8개. 이미지 대신 JSON을 돌려 토큰을 아낀다. 이미지가 필요할 때만 contact sheet 경로를 준다.

| 동사 | 구현 | 불변식 |
|---|---|---|
| `measure` | Pillow+numpy | 결정적. 같은 바이트면 같은 JSON |
| `downscale` | Pillow (nearest/box 선택 명시) | 배율·필터 기록 |
| `mask` | 알파 또는 크로마키 → 실루엣 PNG + 지표 | 원본 불변 |
| `rasterize` | Inkscape CLI (`--export-type=png --export-width`) | SVG 원본 불변, 배율 두 개 |
| `preview` | ImageMagick 또는 Pillow 레시피를 별도 경로에 적용, before/after contact sheet 생성 | RGB-only. alpha plane pre/post SHA-256 동일. 출력은 `out/<run>/` |
| `apply` | `preview`와 동일 파이프라인, 승인된 InstructionRecord만 입력 | 원본 덮어쓰기 금지 |
| `diff` | pre/post measurements 차이 | 결정적 |
| `contact-sheet` | ImageMagick `montage` | 표시용 |

레시피 identity는 `(ordered ops, params, tool versions)`의 canonical hash다. 색 조작(grade) 레시피는 Pillow로 alpha를 분리한 뒤 numpy HSL/linear 연산으로 RGB만 바꾸고 alpha를 되붙인다. 그래야 alpha 불변식이 구현에서 강제된다. ImageMagick은 팔레트 `-remap`과 `montage`에만 쓴다. vibrance는 원어가 없으므로 알고리즘을 명시한다(HSL에서 채도가 낮은 픽셀에 더 큰 가중치를 주는 정의, revision 1). 자세한 카탈로그는 플레이북 6절.

### 9.5 패키징과 스펙 무손실

- 파이썬 코어 `adkit/`가 유일한 구현이다. CLI(`skills/art-direction/scripts/`)와 MCP 서버는 같은 함수를 호출하는 전송층이다.
- SKILL.md는 "언제 어떤 동사를 어떤 순서로"만 말하고 계산을 설명하지 않는다.
- conformance fixture 6장(래스터 2, 스크린샷 2, SVG 2)과 기대 JSON이 `tests/fixtures/`에 있다. CLI와 MCP는 같은 fixture로 같은 출력을 내야 한다. 이것이 P7의 "손실 없음"을 기계적으로 증명한다.
- MCP 승격 조건: 두 번째 호스트가 필요하거나(Codex, Hermes), team canonical이 200건을 넘어 인덱스 상주가 유리해질 때. 그 전에는 MCP를 만들지 않는다.

## 10. 다각도 검토 (six thinking hats, AI 단독 수행)

### 흰 모자: 사실
- 캘리브레이션 쌍 0건. team 층은 비어 있다. `[확실함]`
- v1 어휘 492건 중 규칙 통과 291건, 재편입 포함 약 305건. 판단 어휘 51건, 직접 조작 어휘 68건 중 래스터 툴 직결 약 20건. `[확실함]`
- VLM은 색 정량·밝기 대비에 약하고 절대 점수는 불안정하다. pairwise가 더 안정적이다. `[확실함]`
- OpenRouter 크레딧으로 `voyageai/voyage-multimodal-3.5`를 쓸 수 있고 Cohere Embed v4는 쓸 수 없다. 무료 Nemotron Embed VL이 있다. `[확실함]`
- 같은 컨셉의 완성 스킬은 없다. 부품은 전부 있다. `[확실함]`
- 관찰 레코드는 stdlib만으로 동작한다. 이미지 벡터만 외부 의존을 만든다. `[확실함]`
- 원본은 덮어쓰지 않는다. 롤백 축은 없다. `[확실함]` 사용자 결정

### 빨간 모자: 직감
- 어휘의 `quantification.mode` 설계가 예상보다 훨씬 좋다. 이걸 만든 사람은 이미 이 스킬의 절반을 알고 있었다.
- "판단 루틴화"라는 말은 과장될 위험이 있다. 실제로 루틴화되는 것은 판단의 **기록과 재소환**이지 판단 자체가 아니다.
- 진짜 노동은 stock 사례 40건 저작이다. 코드가 아니라 글이다.
- 팀은 승격 단계를 귀찮아하고 건너뛸 것이다. 그 순간 team 층은 죽는다.
- 이미지 벡터 캐시는 canonical 200건 전까지 장난감이다.

### 검은 모자: 비판
- stock 사례를 우리가 쓰면 우리의 취향이 "업계 표준"으로 둔갑한다. taste-skill의 M13과 같은 죄다.
- VLM 세대가 바뀌면 관찰 레코드의 어조와 region 정밀도가 바뀐다. 다른 관찰자 모델이 낸 레코드끼리 k-NN을 돌리면 거리가 의미를 잃는다.
- 아티스트의 "5%"는 Photoshop vibrance 슬라이더 기준이다. 우리 알고리즘의 5%와 다르다. 숫자가 맞지 않으면 신뢰가 한 번에 무너진다.
- HSL 채도 조작은 지각적으로 균일하지 않다. 붉은 계열과 푸른 계열이 다르게 움직인다.
- 스크린샷은 여러 에셋의 합성이다. 스크린샷 수준 판정을 어느 에셋의 조작으로 되돌릴지 매핑이 없다.
- greenfield에서는 선례가 없어 V2가 거의 항상 `unknown`을 낸다. 사용자는 "이 툴은 아무것도 모른다"고 느낀다.
- 16-bit PNG, premultiplied alpha, indexed PNG에서 tool 유닛이 조용히 망가질 수 있다.
- Inkscape 버전마다 rasterize 결과가 다르다. recipe hash가 같아도 픽셀이 다를 수 있다.
- VLM이 낸 bbox는 부정확하다. evidence region이 증거가 아니라 장식이 될 수 있다.
- 스킬은 Claude Code 안에서만 돈다. 아티스트는 거기 살지 않는다. 도입 자체가 마찰이다.
- 세 배율 × 관찰 = 에셋 하나에 비전 호출 3회. 5000장 배치는 비용이 된다.
- SKILL.md가 taste-skill처럼 1200줄로 자라 컨텍스트를 잠식할 수 있다.

### 노란 모자: 낙관
- 어휘와 연산 레지스트리가 이미 있어 스키마 설계 비용이 거의 0이다.
- ImageMagick·Pillow·Inkscape는 어디에나 있다. 설치 티켓이 거의 안 난다.
- JSONL 레코드는 PR로 리뷰된다. 취향이 코드 리뷰와 같은 절차를 탄다. 아트 바이블이 부산물로 생긴다.
- V0 측정만으로도 CI에서 팔레트·값 범위 드리프트 회귀 검사가 된다. LLM 없이도 가치가 있다.
- pairwise 프로토콜은 신규 아티스트 온보딩 도구를 겸한다.
- stock 사례는 팀 무관이라 커뮤니티 코퍼스가 될 수 있다.
- 생성기 컨텍스트를 선례 키에 넣으면 "이 생성기는 항상 빨강을 과포화시킨다" 같은 생성기별 교정이 공짜로 쌓인다.
- 분리 출력 경로 덕에 자동화 상한을 나중에 올려도 위험이 작다.

### 초록 모자: 창의
- **판단 diff 저장:** 판단문 대신 아티스트가 수락한 before/after 쌍 자체를 저장한다. 델타가 곧 판단이며 언어 매핑 오류가 사라진다.
- **가독성 프로브 합성:** 64px 축소 + 0.5초 노출 시뮬레이션 + 블러를 결정적 대리지표로 만든다. `perception.readability`의 `define_metric`이 자동으로 채워진다.
- **grayscale study 자동 게이트:** 채도 판단 전에 회색조 변환에서 value hierarchy를 먼저 검사한다. 업계 관행을 파이프라인 순서로 고정.
- **house style 재수출:** team canonical에서 S0 형태의 md 요약을 재생성해 SKILL.md에 끼운다. S3가 S0를 낳는다. LLM 프롬프트는 항상 작고 최신이다.
- **pairwise 토너먼트:** 부트스트랩 시 Bradley-Terry식 순위를 소수 비교로 얻는다. 절대 점수 없이 방향을 얻는다.
- **엔진 스크린샷 훅:** 엔진 무관하게 "결정적 상태에서 스크린샷"을 요구하는 계약만 둔다. Unity든 Godot이든 동일한 fixture 계약.
- **관찰자 모델 파티션:** 인덱스를 `observer_model`별로 나누고 교차 검색은 측정치 벡터로만 한다. 검은 모자의 세대 교체 문제를 구조로 해결.
- **에셋 역추적:** 스크린샷 레코드에 `composed_of: [asset_sha256...]`를 넣어 스크린샷 판정을 에셋 후보로 되돌린다. 엔진 훅이 제공하거나 사람이 태깅한다.

### 파란 모자: 종합
첫 구현은 V0+V1, tool 유닛 8동사, stock 어휘 v2, stock 사례 40건, ingest 후보 저장까지다. V2는 fixture와 사례가 준비된 뒤 켠다. 검은 모자의 우려 중 구조로 해결되는 것은 관찰자 모델 파티션, house style 재수출, 판단 diff 저장, 에셋 역추적이며 플레이북에 반영한다. 구조로 해결되지 않는 것은 stock 사례의 취향 편향과 아티스트 도입 마찰이다. 앞의 것은 `evidence_kind: heuristic`과 overridable 표기로 정직하게 남기고, 뒤의 것은 이 검토 범위 밖(프론트엔드)으로 명시한다.

## 11. 사전부검: "6개월 뒤 이 스킬은 완전히 실패했다"

### 11.1 실패 이유 나열

| # | 이유 | 확률 | 영향 |
|---|---|---|---|
| F1 | 승격 단계가 귀찮아 team 층이 6개월 뒤에도 비어 있다 | 고 | 고 |
| F2 | stock 사례가 팀 장르(예: 픽셀 호러)와 맞지 않아 첫 주에 신뢰를 잃는다 | 중 | 고 |
| F3 | 잘못된 판단이 canonical로 올라가 k-NN이 그것을 반복 강화한다 | 중 | 고 |
| F4 | vibrance/saturation 수치가 아티스트의 툴 감각과 달라 숫자 전체를 불신한다 | 중 | 고 |
| F5 | 16-bit·premultiplied·indexed PNG에서 alpha나 색이 조용히 깨진다 | 중 | 고 |
| F6 | 스크린샷 판정이 에셋으로 역추적되지 않아 권고가 실행 불가다 | 중 | 중 |
| F7 | VLM 세대 교체로 과거 관찰 레코드와 비교 불가 | 중 | 중 |
| F8 | SKILL.md가 비대해져 매 호출 컨텍스트를 잠식한다 | 중 | 중 |
| F9 | MCP를 너무 일찍 만들어 CLI와 스펙이 갈라진다 | 중 | 중 |
| F10 | 분리 출력 경로의 산출물이 엔진 임포트 규칙과 맞지 않아 아무도 쓰지 않는다 | 중 | 중 |
| F11 | 개선 여부를 재는 oracle이 없어 회고에서 "효과 불명"으로 폐기된다 | 고 | 중 |
| F12 | 임베딩 API 정책·가격 변화로 꺼졌는데 아무도 degrade를 눈치채지 못한다 | 저 | 저 |
| F13 | Inkscape 버전 차이로 SVG fixture가 CI에서 흔들린다 | 중 | 저 |

### 11.2 상위 리스크와 예방·조기경보

| 리스크 | 예방 조치 | 조기경보 신호 |
|---|---|---|
| F1 team 층 공백 | 승격을 별도 단계가 아니라 미리보기 승인 화면의 체크박스 하나로 만든다. "이 판단을 선례로 남길까요?"가 기본 체크 | 4주 뒤 canonical 0건이면 승격 UX 재설계 |
| F11 oracle 부재 | 첫날부터 human oracle을 정의한다. "같은 에셋 10장에 대해 스킬 제안 vs AD 직접 판단의 방향 일치율"과 "생성 에셋 1차 통과율". 주간 기록 | 2주 연속 일치율 미기록 |
| F3 선례 오염 | canonical 전용 검색, 승격 시 같은 맥락 반대 stance 충돌 차단, `approved_by` 필수, 월 1회 canonical 재검토 목록 자동 생성 | 같은 맥락에서 제안이 한 방향으로만 쏠림 |
| F4 수치 불신 | 레시피 카탈로그에 알고리즘과 "Photoshop 슬라이더와 다름"을 명기. 첫 주에 아티스트가 익숙한 툴로 같은 변화를 만들어 대응표 3점을 잡는다 | "이거 5% 아닌데" 발언 2회 |
| F5 조용한 파손 | `preview`가 alpha plane pre/post 해시와 bit depth·color type을 검사하고 불일치면 실패한다. fixture에 16-bit·premultiplied·indexed PNG 포함 | fixture 실패 |
| F2 장르 부정합 | stock 사례를 전부 `overridable`, `evidence_kind: heuristic`으로 표기하고 첫 세션에서 사례 10건을 팀이 직접 승인·거부하게 한다 | 첫 세션 거부율 50% 초과 |

## 12. 시나리오 × perturbation 별점

별이 많을수록 유리하다. "지불하는 것"과 "지연된 실패"도 별이 많을수록 덜 내고 덜 실패한다는 뜻이다.

### 12.1 기준선: AI 생성 에셋 1차 디렉팅에 적용했을 때

| 시나리오 | 얻는 것 | 지불하는 것 | 지연된 실패 | 공짜 레버리지 |
|---|---|---|---|---|
| S0 메모 파일 | ★★☆☆☆ 즉시 시작, 스타일 문장 정리 | ★★★★★ 거의 0 | ★★☆☆☆ 사례 늘면 붕괴, 검색 불가 | ★★☆☆☆ md가 아트 바이블 |
| S1 관찰 레코드 | ★★★★☆ 측정·선례·CI 회귀 | ★★★★☆ stdlib, 사례 저작 노동 | ★★★★☆ 오염은 승격 게이트로 통제 | ★★★★☆ PR 리뷰, 온보딩, 생성기별 교정 |
| S2 이미지 벡터 | ★★★☆☆ 닮은 선례 | ★★☆☆☆ API·모델·재임베딩 | ★★☆☆☆ 벡터 불투명, 드리프트 | ★★☆☆☆ 캐시 외 없음 |
| S3 하이브리드 | ★★★★★ S1 + 닮은 선례 | ★★★☆☆ S1 + 캐시 관리 | ★★★★☆ S1과 같음(캐시 삭제 가능) | ★★★★★ S1 + 커뮤니티 코퍼스 |
| S4 typed 통합 | ★★★★☆ 감사·재현 최상 | ★☆☆☆☆ API·12타입·계약 | ★★★★★ 구조적으로 가장 안전 | ★☆☆☆☆ 팀 밖으로 못 나감 |

얻는 것의 실체: 생성 에셋의 triage 속도, 그룹 응집 잠금, 생성기별 교정 축적. 지불하는 것의 실체: 에셋당 비전 호출(배율 3개), 승인 시간, stock 사례 40건 저작, 월 1회 canonical 재검토. 지연된 실패의 실체: 선례 오염, 휴리스틱 오적용, 생성기 교체로 선례가 낡음. 공짜 레버리지의 실체: 측정 전용 CI, 레코드가 곧 아트 바이블, pairwise가 곧 온보딩, `generator` 컨텍스트가 곧 생성기 교정.

### 12.2 perturbation 별 회복력

| perturbation | S0 | S1 | S2 | S3 | S4 |
|---|---|---|---|---|---|
| 팀 2→10명, AD 복수 | ★☆ 문장 충돌 | ★★★ 충돌 검사 있음 | ★★ 벡터는 취향을 못 가름 | ★★★ | ★★★★ 권한 모델 |
| 아트 스타일 피벗 | ★★★ 파일 하나 교체 | ★★★ canonical 전량 supersede, stock 유지 | ★ 전량 재임베딩 | ★★★ 캐시 폐기 | ★★ 정책 개정 절차 무거움 |
| 생성기 교체 | ★★ | ★★★★ `generator` 키로 선례 분리 | ★★ | ★★★★ | ★★★ |
| 임베딩 API 중단·가격 변동 | ★★★★★ 무관 | ★★★★★ 무관 | ★ 기능 정지 | ★★★★ V4만 소실 | ★★★★★ 미사용 |
| 아티스트 이탈 | ★★ 암묵지 소실 | ★★★★ 판단이 레코드로 남음 | ★★ | ★★★★ | ★★★★ |
| 에셋 50→5000 | ★ | ★★★ 전수 스캔은 여전히 ms, 비전 비용은 선형 | ★★★ 검색 강점 | ★★★★ | ★★★ API cap |
| 두 번째 호스트 필요 | ★★ 복붙 | ★★★ CLI 공유 | ★★★ | ★★★★ MCP 승격 경로 | ★★ Midori 전용 |
| 입력 비중 SVG로 이동 | ★★ | ★★★ rasterize 두 배율 | ★★ 벡터 원본 임베딩 불가 | ★★★ | ★★ PNG 전용 cap |
| 잘못된 선례 승격 | ★★ 사람이 눈치 | ★★★★ supersede+재구축 | ★ 벡터에 묻힘 | ★★★★ | ★★★★★ |
| 프라이버시 강화(외부 전송 금지) | ★★★★ | ★★★★ V0만 남아도 CI 가치 | ★ | ★★★ API off 한 줄 | ★★★★ egress gate |
| 엔진 교체(스크린샷 성격 변화) | ★★★ | ★★★ 스크린샷 레코드만 재수집 | ★★ | ★★★ | ★ Unity 결합 |
| VLM 세대 교체 | ★★★ | ★★★ observer 파티션 | ★★ | ★★★ | ★★★ 모델 trace |

S3가 모든 열에서 최악이 아니고, S4를 이기는 열이 팀 확장성·API 무관성·호스트 확장 세 곳이다. S4가 이기는 열은 감사와 권한이다. 팀 무관 배포 목표에서는 S3다.

## 13. 확인 안 됨과 열린 질문

- `[확인 안 됨]` OpenRouter 경유 시 Voyage·Google의 zero-retention 정책이 그대로 전파되는지. 팀이 직접 확인.
- `[확인 안 됨]` Claude Code 안에서 배율 3개 관찰의 실제 토큰·지연. fixture 6장으로 측정 필요.
- `[확인 안 됨]` SigLIP 2 CPU 지연과 메모리. API off 팀에 로컬 이미지 벡터를 제공할지는 측정 후 결정.
- `[확인 안 됨]` Inkscape CLI가 팀 머신에 있는지, 버전 고정이 가능한지.
- `[확인 안 됨]` Pillow의 16-bit·premultiplied PNG 처리 경로. fixture로 검증.
- `[확인 안 됨]` stock 사례 40건이 k=3 검색에 충분한지. 가설이며 첫 팀 세션에서 검증.
- `[확인 안 됨]` vibrance 알고리즘 revision 1의 지각적 타당성. 아티스트 대응표 3점으로 보정.
- `[확인 안 됨]` 아티스트가 Claude Code 밖에서 이 스킬에 닿는 경로. 이 검토 범위 밖.
- `[추정]` 판단 diff 저장(초록 모자)이 언어 매핑을 대체할 수 있다는 가설. 승격 화면에 before/after를 함께 저장하는 것으로 시작하고, 매핑 없이도 선례가 검색되는지 관찰.

## 14. 출처

사내·로컬: `hq-gamedev/docs/reviews/2026-08-27-taste-skill-source-backed-adoption-review.md`, `hq-gamedev/docs/superpowers/specs/2026-08-27-typed-visual-art-direction-system-design.md`, `~/Github/agent-sprite-forge` (README, `skills/generate2dsprite/SKILL.md`), `hq-ruby/ad_ta_vocab/*`.

외부 (2026-09-13 확인):
- taste-skill: https://github.com/Leonxlnx/taste-skill
- ImageMagick MCP: https://github.com/bthurlow/imagemagick-mcp , https://github.com/ncipollo/magick-mcp , https://github.com/AeyeOps/mcp-imagemagick
- Inkscape MCP: https://github.com/sandraschi/inkscape-mcp , https://github.com/Shriinivas/inkmcp
- Blender MCP / DCC-MCP: https://github.com/RFingAdam/mcp-blender/ , https://github.com/dcc-mcp
- Claude 스킬 마켓: https://mcpmarket.com/tools/skills/pixel-art-professional , https://crossaitools.com/skills/onewave-ai/claude-skills/color-palette-extractor , https://jimchristian.net/blog/2026/02/27/claude-art-skill-visual-content-system/ , https://piotrtrochim.substack.com/p/teaching-claude-to-create-pixel-art
- 리터칭 에이전트: PhotoAgent https://arxiv.org/html/2602.22809 , PerTouch https://arxiv.org/pdf/2511.12998 , RefineEdit-Agent https://arxiv.org/pdf/2508.17435 , TalkPhoto https://arxiv.org/pdf/2601.01915
- 미학 스코어러: VILA https://arxiv.org/html/2303.14302v2 , Q-Align https://www.emergentmind.com/papers/2312.17090 , UNIAA https://arxiv.org/pdf/2404.09619 , UniQA https://arxiv.org/pdf/2406.01069
- VLM 색 한계: ColorBench https://arxiv.org/pdf/2504.10514 , 색맹검사 https://openreview.net/forum?id=Zn18gRDxhF , Color names in VLMs https://arxiv.org/pdf/2509.22524
- MLLM-as-judge: MM-JudgeBias https://arxiv.org/pdf/2604.18164 , AesBiasBench https://arxiv.org/pdf/2509.11620 , position bias https://aclanthology.org/2025.ijcnlp-long.18/ , Reliability without validity https://arxiv.org/html/2606.19544v1
- 임베딩: https://openrouter.ai/api/v1/embeddings/models , https://openrouter.ai/docs/api_reference/embeddings , https://blog.voyageai.com/2024/11/12/voyage-multimodal-3/ , https://www.spheron.network/blog/multimodal-embedding-models-gpu-cloud-siglip2-jinaclip-cohere/
- 2D 가독성: https://www.nextmars.com/post/when-art-breaks-mechanics-2d-game-art-readability-framework , https://rocketbrush.com/blog/shape-language-in-game-character-design-how-to-make-characters-readable-and-consistent , https://80.lv/articles/defining-environment-language-for-video-games , https://nastyrodent.com/color-theory-for-game-art/
- 인디 pain: https://www.scenario.com/blog/ai-sprite-generator , https://www.seeles.ai/resources/blogs/consistent-ai-game-assets-workflow , https://www.reddit.com/r/gamedev/comments/1r12mtj/ , https://www.reddit.com/r/gamedev/comments/10luj5g/ , https://www.reddit.com/r/gamedev/comments/1che8pu/
