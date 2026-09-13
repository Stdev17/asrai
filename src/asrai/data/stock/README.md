# Stock art-direction vocabulary v2

어느 팀에서도 그대로 쓸 수 있는 게임 아트 디렉션 어휘층. `ad_ta_vocab` v1에서 기계적으로 파생하며, **학습 레이어만** 걷어낸다. **v1은 읽기 전용이고 이 디렉터리에서 수정하지 않는다.**

## 파일

- `vocab.v2.json` — 475개 표제어, 22개 범주. 영어 정본. 항목마다 `origin.entry_sha256`로 v1 원항목을 지시한다.
- `vocab.v2.schema.json` — 위 파일의 JSON Schema (Draft 2020-12).
- `instruction.v2.schema.json` — 설계 요청 스키마. `status`는 `proposed|previewed|approved|applied|rejected|superseded`, `execution`은 `{adapter, binding_resolved, authorized, run_ref}` 실필드다.
- `instruction_examples.v2.json`, `examples/` — 직렬화 예제 8건.
- `locales/<code>.json` — 영어 외 11개 언어. **이 파일들이 번역의 정본이다.** 기여 방법은 `locales/README.md`.
- `validation_report.json`, `manifest.sha256.json`.

## 재생성

```bash
python tools/trim_vocab.py
python tools/review_locales.py
python tools/validate_stock.py --report corpus/stock/validation_report.json
```

`trim_vocab.py`는 `locales/`의 기존 번역을 **덮어쓰지 않는다**. v1은 이 로케일이 아직 본 적 없는 항목을 채울 때만 seed로 쓰인다. 그래서 번역 PR이 재생성으로 날아가지 않는다.

## 걷어낸 것

492 → **475**. 나간 것은 학습 레이어뿐이다.

- `methods` 범주 **17건** — 관찰·모사·능동 회상·썸네일·프롭 스터디 등 연습 과제. 에셋의 속성을 기술하지 않는다.
  나머지 3건은 연습이 아니라 **제작 리뷰 활동**이라 남겼다: `screenshot_audit`(완성 프레임을 축별로 점검),
  `markup`(원본 위에 문제 영역과 수정 의도를 표시), `feedback`(관측값과 판단을 분리하고 다음 변경 하나를 정함).
  이유는 `tools/stock_scope_notes.json`에 있고 항목마다 `scope_note`로 들어간다. 범주에 3건만 남았으므로
  라벨도 v1의 "Observation, copying, variation, recall and review"에서 `Review, markup and feedback`으로 바꿨다.
- `curriculum_weeks` 필드 — 전 항목에서 삭제.
- v1의 출처 장치 — `sources`, `provenance.evidence`, `verified_doc_ids`, `tools`, `coverage_audit`, `technical_verification_sources`, `extraction_contract`. 이들은 한국어 교육 맥락 인터뷰의 인용문·해시·오프셋이지 도메인 어휘가 아니다. 근거가 필요하면 `origin.entry_sha256`으로 v1을 조회한다.
- `operationalization.binding_state`, `is_executable_command`, `normalization_note`.

**도메인 어휘는 2D·3D 구분 없이 전부 남는다.** `material`, `geometry`, `uv_texture`, `rig_animation`, `shader`, `render` 포함 22개 범주. 특정 툴 유닛이 닿는 범위보다 어휘가 넓은 것은 의도한 것이다.

`provenance`의 `term_basis`·`description_basis`·`operationalization_basis`는 남겼다. 다만 `attested_in_in_scope_source`가 가리키는 원 자료는 한국어 교육 맥락 대화이므로, 업계 표준 보증이 아니라 **사용 용례의 기록**으로 읽어야 한다.

`local_meta` 2건은 학습 범주가 아니라 남겼으나, v1 정의가 "in this discussion" / "in this request"로 이 코퍼스 자신을 가리킨다. `scope: uncertain`으로 표시했고 근거는 `tools/stock_scope_notes.json`에 있다.

## 플레이북 §3 Phase 0과 다른 점

1. **범주 삭제 범위.** 플레이북은 8개 범주(3D 6개 + `methods` + `local_meta`) 삭제와 2D 표면 필터를 지시하고 항목 수 300±15를 받아들임 기준으로 두었다. 사용자 지시로 **학습 맥락만 삭제**하도록 바꿨고, 따라서 2D 표면 필터(§3-3)는 근거를 잃어 제거했다. 결과 475건. 리포트 §7.3의 범위 표는 이 결정으로 대체된다.
2. **받아들임 기준.** 항목 수 대신 파생 불변식을 검사한다 — `stock = source − 삭제된 학습 항목`이고, 학습 범주에서 살아남은 항목은 전부 `scope_note`를 갖고 선언된 재편입 목록과 정확히 일치할 것.
3. **i18n.** `i18n.ko.label` 인라인 대신 `locales/<code>.json` 11개. 12개 언어를 인라인하면 `vocab.v2.json`이 1MB 이상 불어난다. `aliases[{text,lang}]`는 명세대로 인라인이다 — ingest가 로케일 파일 없이도 임의 언어 코멘트를 매칭해야 한다.
4. **`quantification.note`.** 항목마다 복제하지 않고 `quantification_profiles[profile_id].note`가 소유한다 (v1에서 이미 중복 제거됨).
5. **`description`.** 새로 번역한 것이 아니라 v1이 이미 영어화되어 있어 `ad_ta_vocab/locales/en.json`에서 왔다. 전 항목 `translated_by: llm`.
6. **`magnitude_basis`에 `example` 추가.** 예제 수치는 선례도 측정도 아니며 `none`으로 두면 "수량 없음"과 구분되지 않는다.
7. **리포트 §7.3의 "조작 어휘 68건"은 오류.** 같은 문서가 준 정의(`direct_with_context` 또는 `measurable_with_context`)로 세면 그 291개 집합에서 104건이다. 판단 어휘 51건은 정확했다. 재현 가능한 정의를 따랐고, 475건 전체에서는 판단 70 / 조작 155다.

수치 테스트 8건과 거절 테스트 9건은 v1과 동일하게 통과한다.

## 한계

- 475건은 v1 코퍼스에서 연습 과제를 뺀 것이다. 이것이 아트 디렉션의 업계 표준 집합이라는 증거는 아니다.
- 설명과 지침은 편집 산문이다. 판단 어휘 70건과 조작 어휘 155건은 `translation_review: needed`이며 사람 확인 전이다.
- 번역은 LLM 작성 대응어다. 표제어 충돌은 해소했고 확인 필요 항목은 `review` 플래그로 표시했다. `locales/README.md` 참조.
- `quantification_profiles`는 수치가 의미를 가지려면 무엇을 고정해야 하는지만 말한다. 권장값을 주지 않으며 여기 어떤 임계값도 규범이 아니다.
- 지각 목표는 수치 속성이 아니다. 대리지표는 대리지표를 측정할 뿐 목표 전체를 증명하지 않는다.
