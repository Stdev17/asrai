# Art-direction skill playbook

> **상태:** 설계 검토 리포트 승인 전 초안. 이 문서는 절차이며 코드가 아니다.
> **작성일:** 2026-09-13
> **근거 문서:** [`docs/review/2026-09-13-art-direction-skill-scenario-review.md`](docs/review/2026-09-13-art-direction-skill-scenario-review.md). 결정 근거는 그쪽에 있고 여기는 실행 순서만 적는다.
> **적용 대상:** GPU 없는 소규모 팀이 AI 생성 또는 수작업 2D 에셋(래스터 PNG, 런타임 스크린샷, SVG)의 1차 아트 디렉팅을 루틴화할 때. 팀 무관(agnostic). hq-gamedev provenance 체계와 무관.
> **전제:** 캘리브레이션 사례 0건에서 출발. stock 층은 `ad_ta_vocab` 정제본 + 저작 사례 40건. team 층은 ingest로만 자란다.

> **개정 2 (2026-09-13, 구현 착수):** 구현 저장소는 `~/Github/asrai`, 구현 계약의 정본은 [`asrai/docs/spec.md`](../asrai/docs/spec.md)다. 이 플레이북은 한국어 근거·절차 문서로 남고, 아래 항목은 spec이 이 문서를 대체한다.
> 1. **3D.** 어휘는 stock에 전부 유지(Phase 0 개정)하고, 메시는 Blender headless 렌더 뷰(render profile)로 L1 증거가 된다. non-goal의 "3D"는 "모델링·리깅·애니메이션 판단"으로 좁힌다.
> 2. **증거 층.** L0(소스 구조) / L1(에셋 렌더) / L2(합성 프레임). 위계·주의·응집은 L2에서만 판정하고 단일 에셋(L1)에서는 `unknown`으로 강제한다. 선례는 층을 넘지 않는다. 엔진 프리팹은 파싱하지 않고 capture contract(PNG + `capture.json`)로 받는다.
> 3. **alpha.** 에셋별 `alpha_policy ∈ preserve | resample_ok | editable`. 레시피는 `alpha_effect ∈ none | resample | edit`를 선언하고 정책이 허용할 때만 apply. `alpha_threshold`, `alpha_defringe` 레시피 추가.
> 4. **첫날 bootstrap.** 레퍼런스에 대한 어휘 설명 후보를 pairwise로 고르게 해 `taste_profile.json`(pairwise 로그의 파생물)을 만들고, oracle의 direction agreement를 첫날부터 잰다.
> 5. **버전 고정.** `uv.lock`(파이썬), `asrai.lock.json`(외부 툴·모델·prompt_rev·코퍼스 해시, `asrai doctor --lock`), 관찰자 모드 `host | api`(api만 진짜 pin, host는 기록과 파티션).
> 6. **호스트.** Claude Code, Codex CLI, OpenCode, Hermes Agent가 1차 타깃. MCP는 Phase 1부터 1급이며 §3 Phase 6의 조건부 규칙과 §12의 해당 항목은 폐기.
> 7. **커뮤니티 stock.** `corpus/packs/<id>/pack.json`으로 확장. 우선순위 team/canonical > packs > stock.
> 8. **레이아웃.** §2는 asrai의 `src/asrai/…`(코퍼스는 패키지 데이터)로 대체.

## 0. 운영 계약

**objective.** 인간 AD/TA가 이미지를 보고 내리는 판단을 (a) 결정적 측정, (b) qualified 관찰, (c) 선례 검색, (d) 결정적 레시피 미리보기의 네 단계로 기록·재소환·실행하게 한다. 판단을 대체하지 않고 판단의 기록과 재사용을 싸게 만든다.

**non-goal.** 이미지 생성·인페인트·재묘사. 3D 모델링·리깅·애니메이션 판단(렌더된 뷰의 실루엣·값·색 판독은 범위 안, 개정 2). 절대 미학 점수. 자동 canonical 교체. 팀별 provenance 연동. 아티스트용 GUI.

**invariants.**
1. 원본 바이트는 불변이다. 모든 산출물은 `out/<run_id>/` 아래 새 파일이다.
2. 색 조작은 RGB 전용이다. decoded alpha plane의 pre/post SHA-256, bit depth, color type이 같지 않으면 실행은 실패다.
3. `proxy_only | qualitative | relational | structural` 어휘에는 `set / add_delta / multiply / relative_delta / percentage_point_delta`를 걸지 않는다. lint가 막는다.
4. 숫자는 `measurements` 또는 `precedent_refs`에서만 온다. VLM이 낸 숫자는 `magnitude_basis: llm`으로 표기되고 자동 적용 대상이 아니다.
5. 검색은 `stock`과 `team/canonical`만 본다. `team/candidate`는 저장만 된다.
6. 삭제는 없다. `supersedes`만 있다. 모든 인덱스는 파생물이며 언제든 재구축된다.
7. 이미지 벡터는 `(model_id, sha256)` 키의 캐시다. 캐시 디렉터리를 지워도 conformance 테스트는 통과해야 한다.
8. 전체 어휘를 프롬프트에 넣지 않는다. `search → get` 순서로 필요한 항목만 넣는다.
9. CLI와 MCP는 같은 파이썬 코어를 호출하고 같은 fixture로 같은 출력을 낸다.
10. stock 사례는 전부 `overridable: true`, `evidence_kind: heuristic`이다. team canonical이 stock과 충돌하면 team이 이긴다.
11. 관찰 레코드는 `observer.model`과 `observer.prompt_rev`를 갖고, 인덱스는 observer별로 분할된다.

**boundary condition.** 입력은 PNG(8/16-bit, indexed 포함)·JPEG·WebP, 런타임 스크린샷, SVG, Blender가 읽는 메시(렌더 뷰로만, 개정 2). 호스트는 Claude Code, Codex CLI, OpenCode, Hermes Agent. 기계 밖으로 나가는 바이트는 Anthropic(비전)과, 켜져 있을 때만, 임베딩 제공자. 이 두 경로 외의 외부 전송은 없다.

**acceptance predicate / evidence.** 각 phase의 acceptance가 모두 통과하고, conformance fixture 6장의 기대 JSON이 CLI에서 재현되며, 13절의 oracle 기록이 2주 이상 존재할 때 "동작한다"고 말한다. 그 전에는 "설계됨"이다.

**stop / escalate / replan.**
- alpha·bit depth·color type 불일치, 레시피 hash 불일치, fixture 실패 → stop. 산출물은 남기되 `status: failed`.
- 승격 시 같은 맥락의 반대 stance canonical 존재 → escalate. 두 레코드를 나란히 인간에게.
- 4주 동안 canonical 승격 0건 → replan. 승격 UX부터 다시.
- 사용량 한도 임박 → 10절의 checkpoint를 쓰고 graceful stop.

## 1. 용어

| 용어 | 여기서의 뜻 | 거짓짝 |
|---|---|---|
| stock 층 | 패키지가 동봉하는 어휘 v2와 사례 40건. 버전 고정 | "업계 표준 정답"이 아니다. 전부 overridable |
| team 층 | 팀이 ingest로 쌓는 사례. `candidate`와 `canonical` | 개인 취향 프로파일이 아니다. 팀 공유 |
| canonical | 인간이 승격해 검색 대상이 된 team 사례 | hq-gamedev의 canonical head와 무관 |
| ObservationRecord | 한 이미지의 측정치·관찰·관계·맥락 | 판단이 아니다. 관찰만 |
| JudgmentCase | 상황 → 판단(축·stance) → 조작 제안의 삼중항 | 점수가 아니다 |
| InstructionRecord | `ad_ta_instruction` v2. 어휘 ID·연산·수량·근거 | 실행 명령이 아니다. 실행은 RecipeRun |
| RecipeRun | 레시피 hash·툴 버전·입출력 해시·diff·상태 | 되돌리기 대상이 아니다. 원본이 그대로 있다 |
| evidence region | 관찰이 가리키는 whole_image 또는 bbox | 격자 패치가 아니다 |
| pairwise | 선례 또는 형제 에셋과의 비교 판단 | 절대 점수가 아니다 |
| operational surface | 조작이 닿는 표면(`color_pipeline`, `vector_paths` 등) | 재질 표면(`material.surface`)이 아니다 |
| magnitude_basis | 수량의 출처: `measurement \| precedent \| human \| llm` | `llm`은 자동 적용 불가 |

## 2. 리포지토리 레이아웃

```text
hq-ruby/
  ad_ta_vocab/                      # v1 원본. 읽기 전용. origin
  corpus/
    stock/
      vocab.v2.json                 # 정제 어휘 (영어 정본, i18n aliases)
      vocab.v2.schema.json
      cases/*.json                  # stock JudgmentCase 40건
      manifest.sha256.json
    team/
      candidate/*.json
      canonical/*.json
      observations/*.jsonl
      house_style.md                # canonical에서 재생성되는 S0 요약
  index/                            # 파생물. .gitignore
    sparse/<observer_model>/...
    vectors/<embedding_model_id>/...
  adkit/                            # 파이썬 코어 (유일한 구현)
    measure.py  recipes.py  corpus.py  retrieve.py  ingest.py  schema/
  skills/art-direction/
    SKILL.md                        # 언제 어떤 동사를 어떤 순서로
    scripts/adkit                   # CLI 전송층
    references/judgment-protocol.md # 5절 사본
    references/recipes.md           # 6절 사본
  mcp/                              # Phase 6 전까지 만들지 않는다
  tests/fixtures/                   # 래스터 2, 스크린샷 2, SVG 2 + 기대 JSON
  out/                              # RecipeRun 산출물. .gitignore
  adkit.toml
```

## 3. 단계 계획

각 phase는 acceptance를 통과해야 다음으로 간다. 순서를 건너뛰지 않는다.

### Phase 0 — stock 어휘 v2 정제 `[2026-09-13 개정, 완료]`

개정 사유: 스톡 어휘는 3D 팀을 포함한 모든 팀이 쓰는 층이므로 도메인 어휘를 범주째 삭제하지 않는다.
학습 맥락만 걷어낸다. 이에 따라 아래 2~4와 받아들임의 항목 수 기준이 바뀌었고, 리포트 7.3절의 2D 범위
표는 대체되었다. P5(3D 제외)는 **vision 유닛의 입력 범위**로만 유효하며 어휘 범위에는 적용하지 않는다.

작업:
1. `tools/trim_vocab.py`가 `ad_ta_vocab/ad_ta_manipulative_vocab.v1.json`을 읽어 `corpus/stock/vocab.v2.json`을 쓴다. v1은 수정하지 않는다.
2. 카테고리 삭제: `methods`의 연습 과제 17건만. 3D 범주(`material, geometry, uv_texture, rig_animation, shader, render`)를 포함한 도메인 어휘는 전부 유지한다. `methods` 안에서도 제작 리뷰 활동인 `screenshot_audit, markup, feedback` 3건은 남기고, 범주 라벨을 `Review, markup and feedback`으로 바꾼다.
3. 표면 필터 없음. 2D 표면 집합으로 거르던 단계는 어휘 범위를 2D로 좁히는 장치였으므로 제거한다.
4. 범위 예외는 전부 `tools/stock_scope_notes.json`에 이유를 한 줄씩 적는다. `reinclude: true` 그룹은 삭제 범주에 속해도 살아남고(`methods` 3건), `scope: uncertain` 그룹은 남기되 표시만 한다(`local_meta` 2건). 모든 예외 항목은 출력에 `scope_note`를 갖는다.
5. 필드 변환: `label_en→label`, `description→description`(영어, `translated_by` 기록), `guidance→guidance`, `search_terms→aliases[{text,lang}]`, `confusable_with[].note_ko→note`. `curriculum_weeks`, `provenance.evidence`, `verified_doc_ids`, `normalization_note`, `operationalization.binding_state`, `is_executable_command` 삭제. `origin: {"corpus":"ad_ta_vocab.v1","entry_sha256":...}` 추가. `quantification.note`는 항목에 복제하지 않고 `quantification_profiles[profile_id].note`가 소유한다. 표제어 표기는 `i18n` 인라인 대신 `corpus/stock/locales/<code>.json` 오버레이가 갖는다 — 이 파일들이 번역의 정본이고 `trim_vocab.py`는 이를 덮어쓰지 않는다.
6. 최상위: `categories[].label_ko→label`, `curriculum_weeks` 삭제. `sources, coverage_audit, tools, technical_verification_sources, runtime_binding_examples, extraction_contract` 삭제. `unit_registry, operation_registry, quantification_profiles, numeric_rules, ambiguous_tokens`는 유지하되 설명 영어화, `ambiguous_tokens`는 유지된 ID만 남김. `metadata`와 `known_limits`는 v2용으로 재작성.
7. `ad_ta_instruction.v1.schema.json` → `corpus/stock/instruction.v2.schema.json`: `intent_ko→intent`, `note_ko→note`, `description_ko→description`, `definition_ko→definition`. `status` enum `proposed|previewed|approved|applied|rejected|superseded`. `execution` 실필드 `{adapter, binding_resolved, authorized, run_ref}`. `changes[]`에 `magnitude_basis`, `precedent_refs` 추가. `axis` 추가.
8. 번역은 LLM 보조로 하되 항목마다 `translated_by: llm|human`을 남기고, 판단 어휘와 조작 어휘는 인간이 읽고 확정한다. 리포트 7.3의 "조작 어휘 68건"은 같은 문서가 준 정의(`direct_with_context` 또는 `measurable_with_context`)와 맞지 않는다 — 그 291개 집합에서 104건이고 475건 전체에서는 155건이다. 판단 어휘는 475건에서 70건.

acceptance:
- v2 스키마 통과. 항목 수는 고정 대역 대신 파생 불변식으로 검사한다 — `stock = source − 삭제된 학습 항목`이고, 학습 범주 생존자는 전부 `scope_note`를 가지며 선언된 재편입 목록과 일치할 것. 현재 475건.
- `*_ko` 키 0건. `curriculum_weeks` 0건. 모든 항목에 `origin.entry_sha256`.
- 로케일별 표제어 충돌 0건. 번역은 `tools/review_locales.py`가 확인 필요 항목에 `review` 플래그를 남기고, 이후는 오픈소스 PR로 받는다 (`corpus/stock/locales/README.md`).
- `ambiguous_tokens`, `confusable_with`가 참조하는 ID가 전부 v2에 존재.
- `validate_export.py`의 lint를 v2 경로로 옮겨 실행해 8건 수치 테스트·9건 거절 테스트가 그대로 통과.
- `manifest.sha256.json` 갱신.

stop: 번역에서 뜻이 갈리는 항목은 `translation_review: needed`로 두고 진행. 삭제 판단이 애매한 항목은 삭제하지 않고 `scope: uncertain`으로 남긴다.

### Phase 1 — tool 유닛

작업:
1. `adkit/measure.py`: Pillow+numpy. 출력 JSON 고정 스키마. 팔레트(k=8 k-means, seed 고정), HSL 히스토그램(p10/p50/p90), 상대 휘도 분포, RMS 대비, 알파 점유율, 실루엣 지표(마스크 면적, convex hull 비, 최소 갭), 엣지 밀도, bit depth·color type. 배율 `[1.0, target, 64px]`.
2. `adkit/recipes.py`: 6절 카탈로그. ImageMagick 호출은 subprocess, 버전은 `magick -version`에서 파싱해 manifest에 기록. Pillow 구현 레시피는 알고리즘 revision을 상수로 둔다.
3. 동사 8개: `measure, downscale, mask, rasterize, preview, apply, diff, contact-sheet`. 각 동사는 JSON을 stdout으로, 이미지는 `out/<run_id>/`에.
4. recipe identity: `sha256(canonical_json(ops, params, tool_versions))`.
5. alpha 가드: `preview/apply`는 실행 전후 alpha plane·bit depth·color type을 비교하고 불일치 시 exit 3.

acceptance:
- fixture 6장에서 `measure` 출력이 기대 JSON과 바이트 동일.
- 같은 입력·레시피·툴 버전으로 `preview` 두 번 → 출력 SHA-256 동일.
- 16-bit PNG, premultiplied alpha PNG, indexed PNG fixture에서 alpha 가드 통과 또는 명시적 실패.
- `rasterize`가 SVG fixture를 두 배율로 만들고 Inkscape 버전을 manifest에 기록.

stop: Inkscape 부재 시 SVG 경로만 `unavailable`로 표시하고 래스터 경로는 계속.

### Phase 2 — stock 사례 40건 저작

작업:
1. 7절 템플릿으로 사례를 쓴다. 출처 표기 `source: readability_framework | taste_skill_M0x | vocab_perceptual_goal`.
2. 군집별 최소 3건: figure-ground/value, silhouette/scale, hierarchy/attention, cohesion/palette, intentional contrast, clutter/density, affordance, pixel 특화, SVG 특화, 생성 시트 특화, VLM 편향 가드.
3. 모든 수치에 `example: true`. `thresholds_not_norms` 규칙을 사례 파일 상단에 반복.
4. 각 사례를 `adkit lint`에 통과시킨다. proxy_only 어휘에 set이 걸려 있으면 저작 오류다.

acceptance:
- 40건 lint 통과. 군집별 3건 이상. 전부 `overridable: true`, `evidence_kind: heuristic`.
- 첫 팀 세션에서 10건을 보여 주고 승인·거부를 기록. 거부율 50% 초과면 사례 재작성 후 재세션.

### Phase 3 — vision 유닛 V0·V1

작업:
1. `SKILL.md` 초안. 트리거, 동사 순서, 금지 사항만. 200줄 상한.
2. V0: `measure`만 호출하는 경로.
3. V1: 판단 어휘 중 P5 범위 항목(리포트 7.3절)에 대해 qualified 관찰. 출력은 ObservationRecord.observations. 형식은 `{term_id, level: asserted|estimated|unknown, region: whole_image|bbox, note}`. 숫자 금지. 제안 금지.
4. 배율 3개를 각각 관찰하고 배율별로 기록한다. 실루엣 관련 어휘는 64px 결과가 우선한다.
5. `observer.model`, `prompt_rev`를 레코드에 고정. 프롬프트 변경은 `prompt_rev` 증가.
6. 스크린샷은 `composed_of: [asset_sha256...]`를 받을 수 있게 필드를 둔다. 없으면 빈 배열.

acceptance:
- fixture 6장에서 ObservationRecord가 스키마 통과. `observations[].note`에 숫자 토큰이 있으면 실패.
- 같은 fixture 3회 관찰에서 `term_id` 집합의 Jaccard가 0.6 이상. 미달이면 프롬프트 수정 후 `prompt_rev` 증가.

### Phase 4 — ingest와 승격

작업:
1. `adkit ingest <image...> --comment "<원문>" --context asset_group=... scene=... state=... generator=...`.
2. 매핑 사다리: aliases 정확 일치 → 부분 일치와 `ambiguous_tokens` 해소 → LLM 제안. `mapped_by`에 단계 기록. 원문 span 보존.
3. 수량 해석: "5%"는 `relative_delta 5`, `baseline_ref`는 ingest 시점 측정치. 수량 없는 코멘트는 stance만.
4. 저장 `team/candidate/`. 검색 제외.
5. 승격 화면: 미리보기 승인 시 "이 판단을 선례로 남길까요?" 체크박스 기본 on. 원문 span, 매핑, 같은 맥락 canonical, 충돌 경고를 한 화면에.
6. 승격 시 `approved_by`, `approved_at` 필수. 충돌 있으면 escalate.
7. 승격 후 인덱스 재구축과 `house_style.md` 재생성.

acceptance:
- ingest 10건 fixture에서 매핑 단계 분포 기록. LLM 단계 비율 50% 초과면 aliases 보강.
- 충돌 fixture(같은 맥락 반대 stance)에서 승격이 막히고 두 레코드가 출력됨.
- 캐시·인덱스 삭제 후 재구축 결과가 삭제 전과 바이트 동일.

### Phase 5 — V2 제안과 임베딩 캐시

작업:
1. 검색: 희소 벡터 = 어휘 ID one-hot ⊕ 정규화 측정치. 맥락 필터(asset_group, scene, state, generator) 우선, k=3.
2. 세 축 판정: `direction_compliance`(stock·canonical 규칙 대비), `asset_cohesion`(그룹 내 pairwise 거리), `intentional_contrast`(맥락 태그로 예외 인정). 축은 절대 합산하지 않는다.
3. InstructionRecord 제안: 방향은 관찰, 크기는 `precedent_refs` 또는 `measurements`. 둘 다 없으면 `quantity` 비우고 `status: proposed`, `magnitude_basis: none`.
4. 임베딩 캐시: `adkit.toml`의 `embedding.enabled`가 true일 때만. 전체 이미지와 실루엣 렌더 두 장. 캐시 키 `(model_id, sha256)`. 패치 임베딩 금지.
5. API off 테스트: `enabled=false`에서 V0~V3 전부 통과, V4만 `unavailable`.

acceptance:
- fixture에서 제안된 InstructionRecord가 lint 통과. `magnitude_basis: llm`인 change가 `apply`에 들어가면 거부.
- 캐시 삭제·모델 ID 변경 시 자동 무효화 확인.

### Phase 6 — MCP 승격 (조건부)

조건: 두 번째 호스트가 필요하거나 canonical 200건 초과. 둘 다 아니면 만들지 않는다.

작업: `mcp/server.py`가 8개 동사를 그대로 툴로 노출. 스키마는 CLI 인자에서 생성. conformance fixture를 MCP 경로로도 실행.

acceptance: CLI와 MCP의 fixture 출력 바이트 동일. 툴 수 8개 초과 금지.

## 4. 일상 루틴: AI 생성 에셋 1차 디렉팅

배치 단위로 돈다. 사람은 3번, 7번, 9번에서만 등장한다.

1. `in/<batch>/`에 에셋과 `context.json`을 둔다. `asset_group, scene, state, generator, generator_prompt_ref, target_scale, composed_of(스크린샷일 때)`.
2. `adkit measure in/<batch> --scales 1.0,target,64` → `observations.jsonl`(measurements만).
3. 생성 시트 사전 검사. 셀 bbox 높이 분산, 셀 가장자리 접촉, 단일 행 시트 여부. 여기서 걸리면 판단 전에 되돌린다. 판단할 가치가 없는 시트에 비전 호출을 쓰지 않는다. 사람은 반려 목록만 본다.
4. V1 관찰. 배율 3개. 결과는 `observations.jsonl`에 병합.
5. 그룹 응집 패스. 배치 내 pairwise 거리(팔레트 EMD, value range 겹침, 엣지 밀도, 실루엣 복잡도). 이상치 목록을 만든다. 맥락 태그가 의도적 대비를 선언한 에셋은 이상치에서 제외하고 `intentional_contrast` 축으로 보낸다.
6. V2가 켜져 있으면 선례 검색 → InstructionRecord 제안 → `preview` → contact sheet. 꺼져 있으면 관찰과 이상치 목록까지가 산출물이다.
7. 리뷰 화면. 에셋마다 제안·before/after·근거(선례 ID, 측정치)·`approve | edit | reject`. "이 판단을 선례로 남길까요?" 기본 on. 사람이 수량을 고치면 `magnitude_basis: human`으로 기록.
8. `adkit apply` 승인분 → `out/<run_id>/<stem>.<recipe8>.png` + `manifest.json`. 원본은 그대로. 엔진 임포트는 `out/`을 읽는다. 이름 규칙은 팀 임포트 규칙과 먼저 맞춘다(리포트 F10).
9. oracle 기록(13절). 사람이 제안과 다른 방향을 골랐으면 그 자체가 canonical 후보다.

예산 감각: 에셋 1장 = 측정 0 토큰, 관찰 3회 비전 호출, 제안 1회 텍스트 호출. 100장 배치는 관찰 300회다. 3번 단계에서 30%를 걸러내는 것이 가장 큰 절감이다.

## 5. 판단 프로토콜

### 5.1 순서 게이트

순서를 바꾸지 않는다. 앞 단계가 `fail`이면 뒤 단계의 색 판단은 보류다.

1. 측정 3배율.
2. grayscale study. 회색조에서 value hierarchy가 읽히는가. 여기서 실패하면 hue·saturation·vibrance 판단은 하지 않는다.
3. 실루엣 64px. 대상이 배경·형제 에셋과 구분되는가. `shape.contour_economy`, `perception.silhouette_readability`.
4. 위계와 주의. 무엇이 먼저 읽히는가. `perception.visual_hierarchy`, `perception.attention`.
5. 그룹 응집. 팔레트·값 범위·엣지 처리가 형제와 같은 언어인가. `perception.style_coherence`, `color.palette_hierarchy`.
6. 의도적 대비. 다름이 진영·씬·상태 태그로 설명되는가. 설명되면 응집 위반이 아니다.
7. 밀도·잡음. `perception.visual_clutter`, `shape.tertiary_detail`.
8. 마지막으로 색. `color.saturation`, `color.vibrance`, `color.hue`, `color.color_temperature`.

### 5.2 방향과 크기의 분업

| 항목 | 누가 정하나 | 근거 필드 |
|---|---|---|
| 무엇이 문제인가(관찰) | VLM + 측정 | `observations[]`, `measurements` |
| 어느 쪽으로(방향, stance) | VLM, 선례가 있으면 선례 우선 | `judgment.stance`, `precedent_refs` |
| 얼마나(크기) | 측정치 또는 canonical 선례의 승인 델타. 없으면 비움 | `quantity`, `magnitude_basis` |
| 적용 여부 | 사람 | `status: approved` |

VLM이 "5% 정도"라고 말해도 그 숫자는 `magnitude_basis: llm`으로 남고 `apply`에 들어가지 못한다. 사람이 그 숫자를 채택하면 `human`으로 바뀐다.

### 5.3 pairwise 형식

```text
term: <vocab id>
A: <asset or precedent ref>   B: <asset or precedent ref>
verdict: prefer_A | prefer_B | equal | unknown
reason: ≤20 words
region: whole_image | bbox[x,y,w,h] on A / on B
scale: 1.0 | target | 64
```

순서 편향 가드: A/B와 B/A를 둘 다 묻고 verdict가 뒤집히면 `unknown`. 숫자 점수는 쓰지 않는다.

### 5.4 qualified level

- `asserted`: 측정치가 뒷받침하거나 세 배율 모두에서 같은 관찰.
- `estimated`: 측정치 없는 모델 관찰, 또는 두 배율에서만 일치.
- `unknown`: 배율 간 불일치, 증거 영역 없음, pairwise 뒤집힘.

`unknown`은 절대 change가 되지 않는다. 측정 요청이나 사람 질문으로 바뀐다.

### 5.5 세 축

- `direction_compliance`: stock 규칙과 team canonical에 대한 일치. 5.1의 2~4, 7, 8단계 결과.
- `asset_cohesion`: 같은 `asset_group` 안의 pairwise 거리와 언어 일치. 5단계.
- `intentional_contrast`: 맥락 태그가 설명하는 차이. 6단계. 태그가 없으면 `unknown`이지 `fail`이 아니다.

세 축은 각각 `pass | warn | fail | unknown`이고 합산하지 않는다.

### 5.6 VLM 편향 가드

- 붉은 계열 편향: "너무 빨갛다" 관찰은 hue 히스토그램 측정이 없으면 `estimated`로 강등.
- 밝기 둔감: 밝기·어둡기 관찰은 상대 휘도 분포 인용이 없으면 `estimated`.
- 색 정량 불능: 채도·vibrance의 크기는 VLM이 정하지 않는다(5.2).
- 순서 편향: 5.3의 양방향 질문.

## 6. 레시피 카탈로그 v1

두 클래스가 있다. `grade`는 RGB 전용이며 alpha plane 불변식을 강제한다. `resample`은 alpha가 바뀌는 것이 정상이며 `alpha_policy: resampled`를 선언하고, 자동 적용이 없다. 이 구분은 첨부 스펙의 "alpha-bearing resize/crop 전면 거부"를 픽셀 아트 교정을 위해 완화한 것이다.

| 레시피 | 클래스 | 어휘 ID | 구현 | 파라미터 | 주의 |
|---|---|---|---|---|---|
| `recipe.saturation.rev1` | grade | `color.saturation` | numpy HSL. `S' = clamp(S × (1 + d/100))` | `d` percent_relative, −50..50 | Photoshop 슬라이더와 다름 |
| `recipe.vibrance.rev1` | grade | `color.vibrance` | numpy HSL. `S' = clamp(S × (1 + k(1−S)))`, `k = d/100`. 저채도 픽셀에 더 크게 | `d` −50..50 | vibrance 원어 없음. 정의가 곧 레시피 |
| `recipe.hue_shift.rev1` | grade | `color.hue` | `H' = (H + deg) mod 360` | `deg` −180..180 | 피부색 보호 없음 |
| `recipe.exposure.rev1` | grade | `color.exposure` | sRGB→linear, `× 2^EV`, →sRGB | `EV` −2..2 | linear 변환 고정 |
| `recipe.levels.rev1` | grade | `color.gamma` | per-channel `in_black, in_white, gamma` | 0..255, 0.5..2.0 | value 판단의 실행면 |
| `recipe.contrast.rev1` | grade | `color.tone_mapping` | 중회색 기준 S-curve, strength | `s` −1..1 | `value.value_contrast`(proxy_only)의 실행 대리 |
| `recipe.color_temperature.rev1` | grade | `color.color_temperature` | RGB gain warm/cool | `t` −100..100 `declared_tool_unit` | K 단위 아님. 광원 모델 없음 |
| `recipe.palette_remap.rev1` | grade | `color.color_grading` (`set_relation` palette ref) | Pillow alpha 분리 → `magick -remap palette.png` → 병합 | `palette_ref`, `dither on/off` | dither는 결정적 방식만 |
| `recipe.edge_strengthen.rev1` | grade | `shape.edge_control` | alpha 마스크 경계 안쪽 `w`px를 어둡게 블렌드 | `w` 1..3 px, `strength` | alpha 있는 스프라이트만 |
| `recipe.pixel_snap.rev1` | resample | `pixel_sprite.pixel_snapping` | 격자 `g`로 nearest 재양자화 | `g` px, `offset` | alpha 변함. 승인 필수 |
| `recipe.downscale_preview.rev1` | resample | `pixel_sprite.internal_resolution` | box 또는 nearest, 명시 | `scale`, `filter` | 미리보기·측정 전용 |
| `recipe.svg_rasterize.rev1` | resample | `pixel_sprite.rasterization` | `inkscape --export-type=png --export-width=W` | `W` 두 값 | Inkscape 버전 manifest 기록 |
| `recipe.svg_stroke.rev1` | vector_edit | `vector.stroke` | `stroke-width` 속성 set, 선택자 | `w` svg_user_unit | 새 SVG 파일. 원본 불변 |

모든 grade 레시피는 `magnitude_basis`가 `measurement | precedent | human`일 때만 `apply` 가능하다. 두 레시피를 연쇄할 때 순서는 5.1의 게이트 순서를 따른다(값 → 색).

첫 주 과제: 아티스트가 익숙한 툴에서 "채도 +10 느낌"을 만들고 우리 레시피로 같은 느낌이 나는 `d`를 세 점 찾아 대응표를 `corpus/team/tool_correspondence.json`에 둔다. 이 표가 없으면 숫자 불신(리포트 F4)이 온다.

## 7. stock 사례 템플릿과 첫 12건

### 7.1 템플릿 (`case.v2`, 영어 정본)

```json
{
  "schema_version": "case.v2",
  "id": "case.figure_ground_value_first",
  "tier": "stock",
  "evidence_kind": "heuristic",
  "overridable": true,
  "source": "readability_framework",
  "title": "When figure-ground fails, fix value contrast before saturation",
  "scope": { "inputs": ["raster", "screenshot"], "context_tags": [] },
  "situation": {
    "observations": [
      { "term_id": "perception.figure_ground", "level": "estimated", "stance": "fail" }
    ],
    "measurements": [
      { "metric": "subject_vs_surround_luminance_delta", "op": "lt", "value": 0.12, "example": true }
    ]
  },
  "judgment": {
    "axis": "direction_compliance",
    "stance": "avoid",
    "terms": ["perception.figure_ground", "value.value_contrast"],
    "rationale": "Lightness contrast is the primary depth and priority signal in 2D; saturation cannot substitute for it."
  },
  "instruction": {
    "changes": [
      { "term_id": "value.value_contrast", "operation": "propose_variation",
        "recipe_hint": ["recipe.contrast.rev1", "recipe.exposure.rev1"], "magnitude_basis": "precedent" }
    ]
  },
  "acceptance": [
    { "kind": "numeric", "metric": "subject_vs_surround_luminance_delta", "op": "gte", "value": 0.12, "example": true },
    { "kind": "human", "description": "Subject reads first at 64px in grayscale." }
  ],
  "do_not": ["Do not raise saturation to repair figure-ground."],
  "i18n": { "ko": { "title": "figure-ground 실패 시 saturation보다 value contrast 먼저" } }
}
```

수치는 전부 `example: true`다. team canonical이 같은 `id`를 `supersedes`로 덮으면 stock 사례는 검색에서 빠진다.

### 7.2 첫 12건 (요약)

| id | 상황 | 판단(축·stance) | 조작 제안 / recipe_hint | 수용 조건 |
|---|---|---|---|---|
| `case.grayscale_gate_first` | 어떤 색 판단 요청이든 | direction, gate | `value.grayscale` measure → 위계 확인 후 진행 | 회색조에서 주체가 먼저 읽힘(human) |
| `case.figure_ground_value_first` | figure-ground fail, 휘도 델타 낮음 | direction, avoid | `value.value_contrast` propose → contrast/exposure | 휘도 델타 ≥ 예시값, 64px 판독 |
| `case.silhouette_collapse_remove_tertiary` | 64px에서 실루엣 지표 붕괴 | direction, avoid | `shape.tertiary_detail` propose_variation(감소) | 64px 마스크 convex 비 회복(예시) |
| `case.dull_is_distribution_not_mean` | "칙칙하다" 관찰 | direction, contextual | 먼저 `color.saturation` p50/p90과 value range measure. 값 범위 좁으면 levels, 아니면 vibrance 소폭 | 사람 pairwise before/after |
| `case.affordance_denial_non_actionable` | 비상호작용 오브젝트가 상호작용 오브젝트보다 채도·대비 높음 | direction, avoid | 비상호작용 대상에 `color.saturation` relative_delta(음수, 예시 −10) | 상호작용 대상이 먼저 읽힘(human) |
| `case.palette_hierarchy_outlier_in_group` | 그룹 팔레트와 EMD 큼 | cohesion, warn | `color.color_grading` set_relation → palette_remap | EMD ≤ 예시값, 사람 확인 |
| `case.intentional_contrast_by_tag` | 차이가 크지만 진영·상태 태그 있음 | contrast, pass / cohesion, n/a | 없음 | 태그가 차이를 설명(human) |
| `case.icon_stroke_negative_space` | 24px 아이콘, stroke < 2px 또는 negative space 비 낮음 | direction, avoid | `vector.stroke` set(SVG) 또는 `pixel_sprite.pixel_snapping` | 24px에서 역할 판독(human) |
| `case.pixel_snap_before_judging` | 픽셀 아트인데 격자 이탈 감지 | direction, gate | `recipe.pixel_snap.rev1`(resample, 승인 필수) 후 재관찰 | 격자 이탈 0 |
| `case.svg_judge_at_two_scales` | SVG 입력 | direction, gate | `recipe.svg_rasterize.rev1` 두 배율 후 관찰 | 두 배율 관찰 term 집합 일치 |
| `case.sheet_scale_drift_first` | 생성 시트 셀 bbox 높이 분산 큼 | direction, gate | 색 판단 전 반려. 생성기 재실행 권고 | 분산 ≤ 예시값 |
| `case.vlm_red_bias_guard` | "너무 붉다" 관찰, hue 히스토그램 미인용 | direction, unknown | 없음. hue measure 요청 | 측정 후 재판정 |

나머지 28건은 같은 군집(위계·주의, 밀도·잡음, 스크린샷 역추적, 생성기별 교정, 값·highlight/shadow, 온도·tint, 엣지 처리 일치, 로컬라이제이션 안전 구도)을 3건씩 채운다.

## 8. 설정: API on/off와 프라이버시

```toml
[observer]
model = "claude-<pinned>"
prompt_rev = "v1"
scales = [1.0, "target", 64]

[embedding]
enabled = true
provider = "openrouter"
model = "voyageai/voyage-multimodal-3.5"   # 실험: "nvidia/llama-nemotron-embed-vl-1b-v2:free"
cache_dir = "index/vectors"

[egress]
allow_external_embedding = true            # false면 embedding.enabled를 무시하고 끈다

[paths]
inbox = "in"
out = "out"
corpus = "corpus"
```

기계 밖으로 나가는 것: 관찰 시 이미지 바이트 → Anthropic. `embedding.enabled`일 때 전체 이미지와 실루엣 렌더 → 임베딩 제공자. 그 외 없음. 측정치·레코드는 로컬이다.

팀이 확인할 것: OpenRouter 경유 시 Voyage·Google의 zero-retention 정책이 그대로 적용되는지. 확인 전에는 `allow_external_embedding=false`가 안전한 기본값이며, 리포트 5.2절의 셋째 열로 동작한다.

## 9. 학습과 롤백 절차

- 승격: `adkit promote <candidate_id> --by <name>`. 충돌 검사 → canonical 이동 → 인덱스 재구축 → `house_style.md` 재생성.
- 강등: `adkit demote <canonical_id> --reason "<...>"`. `superseded_by: null`, `status: demoted`. 인덱스 재구축.
- 대체: `adkit supersede <old_id> <new_candidate_id>`. 옛 레코드는 남고 검색에서만 빠진다.
- 재구축: `adkit reindex`. 결정적. 삭제 전후 바이트 동일해야 한다.
- 캐시: `adkit cache purge [--model <id>]`. 기능 저하는 V4 하나.
- 월 1회: `adkit review-list`가 같은 맥락에서 제안이 한 방향으로만 쏠린 canonical 목록을 낸다. 사람이 다시 본다.
- 금지: 레코드 병합·요약·수정. 새 레코드와 `supersedes`만.

## 10. 체크포인트와 graceful stop

에이전트 세션이 길어지거나 사용량 한도가 가까우면 다음을 쓰고 멈춘다. 위치는 프로젝트 메모리 디렉터리(`~/.claude/projects/<repo>/memory/`)와 레포의 `corpus/team/CHECKPOINT.md` 둘 다.

```text
phase: <0-6>
last_acceptance_passed: <목록>
in_progress: <작업 한 줄>
pending_human: <질문 또는 승인 대기>
next_command: <바로 실행할 명령 한 줄>
fixtures_state: <통과/실패 목록>
```

재개 시 CHECKPOINT부터 읽고, 통과한 acceptance는 다시 하지 않는다. 미해결 결정 프로브는 다시 묻지 않는다(리포트 2절이 정본).

## 11. conformance 테스트 목록

1. fixture 6장 `measure` 바이트 동일.
2. grade 레시피 결정성: 같은 입력·레시피·툴 버전 두 번 → 같은 해시.
3. alpha 불변: grade 레시피 전후 decoded alpha plane SHA-256, bit depth, color type 동일. 16-bit·premultiplied·indexed fixture 포함.
4. resample 레시피는 `alpha_policy: resampled` 없이는 실패.
5. lint: proxy_only 어휘에 set/delta → 거부. delta에 `baseline_ref` 없음 → 거부. `magnitude_basis: llm` → `apply` 거부.
6. 검색 범위: candidate가 검색 결과에 나오면 실패.
7. 재구축 결정성: 인덱스·캐시 삭제 후 재구축 결과 바이트 동일.
8. 캐시 독립: `index/vectors` 삭제 후 1~7 통과, V4만 `unavailable`.
9. observer 파티션: 다른 `observer.model` 레코드가 같은 희소 인덱스에 섞이지 않음.
10. 충돌 차단: 반대 stance canonical 존재 시 promote 실패와 두 레코드 출력.
11. 관찰 스키마: `observations[].note`에 숫자 토큰 없음. 세 배율 모두 존재.
12. CLI/MCP 동일 출력(Phase 6 이후).
13. 원본 불변: 어떤 동사도 `in/` 아래 파일의 mtime·해시를 바꾸지 않음.

## 12. 하지 말 것

- 이미지 생성·인페인트·재묘사를 레시피에 넣지 않는다.
- 절대 미학 점수를 내지 않는다. 축을 합산하지 않는다.
- 격자 패치 임베딩을 하지 않는다.
- 전체 어휘나 전체 사례를 프롬프트에 넣지 않는다.
- stock 사례의 수치를 팀 규범으로 승격하지 않는다.
- `unknown`을 change로 바꾸지 않는다.
- 레코드를 삭제·병합·요약하지 않는다.
- MCP 툴을 8개 넘게 노출하지 않는다(개정 2: MCP는 Phase 1부터 존재한다).
- SKILL.md를 200줄 넘게 키우지 않는다. 넘치면 `references/`로.
- 스크린샷 판정을 `composed_of` 없이 에셋 조작으로 바꾸지 않는다.

## 13. oracle: 효과 측정

첫날부터 `corpus/team/oracle.jsonl`에 주 1회 기록한다. 기록이 없으면 회고에서 이 스킬은 "효과 불명"으로 폐기된다(리포트 F11).

| 지표 | 정의 | 목표(가설) |
|---|---|---|
| direction agreement | 같은 에셋 10장에서 스킬 제안 stance와 AD 직접 판단의 일치율 | 4주 뒤 70% |
| first-pass acceptance | 생성 에셋 배치 중 1차 디렉팅 후 승인 비율 | 도입 전 대비 상승 |
| precedent hit | V2 제안 중 canonical 선례를 근거로 든 비율 | canonical 40건 시점에 50% |
| unknown rate | 관찰 중 `unknown` 비율 | 감소 추세, 0은 의심 |
| triage time | 배치 100장 사람 리뷰 시간 | 도입 전 대비 감소 |
| canonical growth | 주간 승격 건수 | 4주 연속 0이면 replan |

목표는 가설이며 첫 측정 후 갱신한다.
