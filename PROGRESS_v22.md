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
- [ ] 3. 테이크 고르기 (eval8) → prep_narr
- [ ] 4. 음악 178초 맞춤 (scripts/music_fit.py) → audio/bgm_v22_*.wav
- [ ] 5. 소리 섞기 (mix9, 에코 없음) → audio/master_v22_*.wav
- [ ] 6. 화면 빌드(JV=gv) + 전체 렌더 1회
- [ ] 7. 미리보기 3개 합치기 → deliverables/v22/
- [ ] 8. 검수: 화면 튐, 받아쓰기, 스냅샷
