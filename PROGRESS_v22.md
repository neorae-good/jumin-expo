# v22 작업 진행 기록 (2026-11-03 밤 시작)

구성: 2안(JV=gv) 화면 고정 + L12 A안 문장, 남자 성우 "힘차게"(eleven_v4, [energetic], stability 0.3; L15는 태그 없음)

| 버전 | 음악 | 성우 (voice id) |
|---|---|---|
| 1 | 스포츠중계 (audio/src_v22_1_sports.wav) | Yohan (4JJwo477JUAx3HV0T7n7) |
| 2 | Bright New Dawn (audio/src_v22_2_dawn.wav) | Dennis (KlgjGxt7IJPLKAwBQbVn) |
| 3 | 포크 = New Morning Energy 3분 (audio/src_v22_3_folk.wav) | David (v1jVu1Ky28piIPEJqRrm) |

## 단계
- [x] 0. 음악 원본 복사
- [x] 1. L12 A안 문장 반영 (script6.json, caplines6.json)
- [x] 2. 녹음 3명 × 15줄 × 3테이크 (scripts/tts_voice.py)
- [x] 3. 테이크 고르기 (eval8) → prep_narr
- [x] 4. 음악 178초 맞춤 (scripts/music_fit.py) → audio/bgm_v22_*.wav
- [x] 5. 소리 섞기 (mix9, 에코 없음) → audio/master_v22_*.wav
- [x] 6. 화면 빌드(JV=gv) + 전체 렌더 1회
- [x] 7. 미리보기 3개 합치기 → deliverables/v22/
- [x] 8. 검수: 화면 튐, 받아쓰기, 스냅샷

### 4단계 메모 (음악 맞춤)
- 스포츠중계 134 BPM: 29.7초와 143.3초 부근에서 8마디씩 반복. 끝 화음이 176.6초에 끝남(마지막 1.4초는 화면 페이드와 같이 정적)
- Bright New Dawn 124 BPM: 42.6초에 4마디×3, 85.5초에 8마디, 117.9초에 1마디 반복. 끝 178.1초
- 포크 130 BPM: 원래 18.8초 구간 전환이 본편 시작(19초)과 거의 일치. 147.3초에서 5마디, 163.4초에서 3마디를 잘라냄. 끝 177.7초
- 늘리거나 줄이는 처리(타임 스트레치)는 하지 않았고, 마디 단위 반복·잘라내기만 함

### 3·5단계 메모
- Dennis L03은 "창원"이 "장원"으로 들려 3번 더 녹음(d~f)하고 e를 씀. L05는 "모여"가 "뭐여"로 들리는 b 대신 c를 씀
- 소리: audio/master_mix9_v22_1.wav(Yohan+스포츠중계), _v22_2(Dennis+Bright New Dawn), _v22_3(David+포크), 음량 -13.6~-14.0 LUFS

### 6·7단계 메모
- 화면: `CAPV=yohan,dennis,david JV=gv python3 scripts/build8.py` → video/renders/jumin-expo-v22.mp4 (전체 렌더, 3 workers)
- 소리를 섞을 때 남자 목소리가 음악에 묻혀 몇 단어가 다르게 들려서, 말소리 대역 줄이기 목표를 11dB에서 14dB로 올림(`CARVE_TARGET=14`)
- 테이크 교체: Dennis L05 → a, David L06 → c, L12 → b
- 결과: deliverables/v22/주민자치박람회_주제영상_v22_{1_Yohan_스포츠중계,2_Dennis_BrightNewDawn,3_David_포크}_미리보기.mp4
