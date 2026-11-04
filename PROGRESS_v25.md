# v25 작업 기록 (2026-11-04 밤): 미리보기 6개

| # | 성우 | 내레이션 |
|---|---|---|
| 1 | Juan | 지금처럼(평균 속도 + 억양 설계) |
| 2 | Henry | 지금처럼 |
| 3 | Haechan | 지금처럼 |
| 4 | Juan | 힘찬(같은 속도, 힘을 더) |
| 5 | Henry | 힘찬 |
| 6 | Haechan | 힘찬 |

공통: 2안 화면, 음악 "Our Shared Neighborhood" -6dB, 15초 타이틀은 더 강하게, L12 A안, 압축 약하게.
음악: 원곡 도입부를 늘려 드럼이 19초에 자연스럽게 / 실 클로즈업 드럼·베이스 빼기 / 천 던지기 정점 → 끝 사진에서 내려앉음 → 타이틀 원곡 마무리, 페이드 길게.

## 단계 (모두 완료)
- [x] 1. 음악: `scripts/music_fit_v25.py` → audio/bgm_v25.wav (도입부 2마디×2 반복: 베이스 17.3초, 드럼 19.8초, 본론 78.2초에 6마디 반복, 끝 45초 원곡)
       → Demucs → `scripts/stem_arrange_v25.py` → audio/bgm_v25_arr.wav (실 클로즈업 드럼·베이스 빼기, 139.2초 +1.5dB 정점,
       149.6→162.4초 드럼 -6/베이스 -3으로 내려앉음, 174~178초 페이드)
- [x] 2. Haechan "지금처럼" (`tts_v24.py haechan24`, `pick_v25.py full`). L12·L15·타이틀은 너무 높아 [warm][proud]/[proud]로 재녹음(L12j, L15k, LTj)
- [x] 3. 15초 타이틀 강하게: Juan LTf(+6.2음), Henry LTe(+4.8음), Haechan LTj(+5.6음)
- [x] 4. "힘찬" (`tts_v25.py strong`, `pick_v25.py strong`): [energetic] 없이 [confident]/[proud][confident]. 길이는 "지금처럼"의 0.90~1.00배
       L15는 Juan·Haechan이 +12음 이상이라 "지금처럼" 구호 사용(juanS/haechanS L15z)
- [x] 5. 섞기 `NARR_LIGHT=1 CARVE_TARGET=14 CARVE_MAX=12 MUSIC_DB=-6`, 음악 bgm_v25_arr.wav. 받아쓰기로 교체: Haechan L03 c, juanS L10 a, henryS L08 a
       Haechan L04는 자막 시간 안에 끝나도록 d(4.3초)
- [x] 6. 화면: 재렌더 없이 v22 렌더 사용(6개 모두 말하는 동안 자막 유지 확인)
- [x] 7. 미리보기 6개 deliverables/v25/, 음량 -14.1~-14.2 LUFS, 받아쓰기 narr/stt_v25_*.txt
- [x] 8. GitHub 저장
