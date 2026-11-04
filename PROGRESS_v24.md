# v24 작업 기록 (2026-11-04)

- 음악: "Our Shared Neighborhood" (수노, 112 BPM, 157.6초) → `python scripts/music_fit.py 4_new` → audio/bgm_v22_4_new.wav
  - 본론 72.9초(8마디)·55.8초(2마디) 반복, 마지막 45초는 원곡 그대로. 원곡 끝 여운 0.9초는 페이드 구간에서 잘림
- 성우 2명, 억양 설계 녹음 `scripts/tts_v24.py` (4테이크) + 고르기 `scripts/pick_v24.py`
  - 보통 줄: 태그 없음, 안정도 0.35 / L01·L02: [warm] / 타이틀·L03·L08·L13·L14: [warm][proud] / L12·L15: 강하게
  - 목표 높이(보통 줄 대비): 보통 ±2음, 타이틀·L03·L08 +1~3.5, L12 +2~5, L13·L14 +0.5~3, L15 +3~9
  - Juan L12·L15는 [proud][excited]/[proud]가 +10~12음으로 너무 높아 어제 녹음한 [warm][proud] 테이크(L12e +2.4, L15e +8.0) 사용
  - Henry L12는 숨소리·높이 문제로 [warm][proud] 3번 재녹음 → L12f(+1.2음, 숨소리 없음)
  - 숨소리 잡힌 테이크 교체: Henry L03 d, L11 c. 음악 속 받아쓰기로 L05 교체(Juan b, Henry b). Juan L11 c(자막 시간 안에 끝나도록)
- 섞기: `NARR_LIGHT=1 CARVE_TARGET=14 CARVE_MAX=12`, 음악 Juan -3dB / Henry -6dB
  → audio/master_mix9_v24_juan.wav (-14.0 LUFS), master_mix9_v24_henry.wav (-14.2 LUFS)
- 화면: v22 렌더 재사용(모든 줄에서 말하는 동안 자막 유지 확인)
- 결과: deliverables/v24/주민자치박람회_주제영상_v24_{Juan_음악-3dB,Henry_음악-6dB}_미리보기.mp4
- 받아쓰기: narr/stt_v24_juan.txt, stt_v24_henry.txt (L05 교체 전 결과. 교체 후 L05는 별도 확인 완료)
