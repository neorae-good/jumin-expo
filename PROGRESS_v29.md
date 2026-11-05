# 현재 상태 (2026-11-04 밤, v29) — 다음 작업자/다음 대화가 여기서 이어받기

## 확정된 것
- 화면: 2안 (Grok 영상 초반·끝), `CAPV=yohan,dennis,david JV=gv python3 scripts/build8.py` → 렌더본 `video/renders/jumin-expo-v22.mp4`(저장소에 없음, 이 세션 컨테이너에만 있음)
- L12 문장 A안, 15초 타이틀 내레이션(LT, 자막 없음), L15 강하게
- 최신 음악: 담당자가 수노에서 2:58로 만든 "Our Shared Neighborhood (Edit)" → audio/src_v29_osn_edit.mp3 (저장소에 없음, 담당자 보유)
- 음악 연출(자르기 없음, 악기별 크기만):
  `python3 -m demucs -n htdemucs -d cpu -o audio/stems audio/bgm_v29.wav`
  `MID_LIFT=1.2 CLIMAX=1.6 HEADROOM_DB=6 python3 scripts/stem_arrange_v26.py bgm_v29 bgm_v29_arr.wav`
  시간표: 0~0:17 잔잔 / 1:15~1:23 조용 / 1:24~2:10 격양 / 2:10~2:13 살짝 조용 / 2:13~2:42 가장 격양 / 2:42~ 조용, 174~178초 페이드
- 섞기(원곡 대비 음악 -4dB = 여유 6dB 되돌림 +2):
  `NARR_LIGHT=1 CARVE_TARGET=14 CARVE_MAX=12 MUSIC_DB=2 python3 scripts/mix9.py <성우폴더> v29_<성우폴더> off 0.4 bgm_v29_arr.wav`
- 영상 합치기: v22 렌더본 + audio/master_mix9_v29_*.wav (8Mbps 미리보기)

## 최신 결과물 (deliverables/v29/, 담당자에게 전달함)
- Juan / Henry / Haechan "힘찬" 내레이션 × (소리만 mp3, 영상 미리보기 mp4)
- 성우 폴더: narr/v8p/juanS, henryS, haechanS (테이크 선택은 narr/v8/picks.json)
- 받아쓰기: narr/stt_v29_*.txt (알려진 표기 차이만 남음)

## 다른 후보 (이전 결과물)
- v25: 같은 3명 "지금처럼"(juan24/henry24/haechan24) + "힘찬", 음악 "Our Shared Neighborhood" 2:38판 편곡
- v22~v23: Yohan/Dennis/David, Juan 초기판

## 담당자 요청 방식 / 지켜야 할 것
- 음악은 곡 중간을 잘라 잇지 않는다(어색하다는 지적 반복). 길이가 모자라면 담당자가 수노에서 늘려 옴
- 녹음 늘이기·줄이기(타임 스트레치) 금지, eleven_v4는 speed 무시 → 지시 태그로 조절
- "힘찬" = 빠르게가 아니라 힘 있게(같은 속도). [energetic]은 빨라지고 음이 너무 높아짐
- 유료 API(ElevenLabs, Grok)는 먼저 묻고 쓴다. ElevenLabs 누적 약 13,700 / 40,000자
- 결과물: 평소 에코 없음 미리보기, 요청 시 상영용(crf 17)+미리보기
- 상영 2026-11-12, 최종 검수 마감 2026-11-06

## 최종본 (2026-11-05, 담당자 확정: 1안 = Juan 힘찬)
- deliverables/final/주민자치박람회_주제영상_최종_Juan_힘찬_상영용.mp4 (crf 17) / _미리보기.mp4 (8Mbps) — 저장소에 없음
- 화면: `CAPV=juanS JV=gv python3 scripts/build8.py` 전체 렌더 → video/renders/jumin-expo-v29-juan.mp4
  + 끝 하늘 영상 페이드 복구 후 160~178초만 다시 렌더(`render_part.py 160 178`)해서 4800프레임에서 이어붙임
- 소리: audio/master_mix9_v29_juanS.wav
- 주의: 하늘 영상(#g9-w)을 #s6bg 밖으로 옮기면서 1초 겹침 전환이 사라졌던 것을 main5.js에서 직접 페이드로 되살림
