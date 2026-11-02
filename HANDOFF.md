# 2026년 제8회 경상남도 주민자치 박람회 주제영상: 작업 인수인계

이 폴더 하나로 영상을 다시 빌드·렌더하고, 소리를 다시 섞고, 내레이션을 다시 녹음할 수 있습니다.
2026-11-02 기준으로 정리했습니다. 이전 작업자의 계정(ElevenLabs·Grok·구글)은 이제 쓰지 않습니다.
ElevenLabs·Grok은 새 담당자 본인 계정을 연결해서 씁니다.

## 1. 지금 상태

- 영상: 2분 58초(178초), 1920×1080, 30fps. 조각보 콘셉트. 경남 18개 시군 사진이 조각보 천 위에 한 조각씩 놓이고, 하나의 천이 되어 하늘로 날아가는 흐름입니다.
- 최신본은 **v20**입니다(아래 "v20 반영 내용"). 아래 v19 설명은 이력으로 남깁니다.
- v19: 목소리는 2번(ElevenLabs "Kanika", `p9aflnsbBe1o0aDeQa97`)으로 정했고, 울림만 다른 두 가지 소리로 만들었습니다.
  - `deliverables/…v19_목소리2_에코줄임_상영용.mp4`: 울림 −26dB, 0.4초. 공기감만 살짝 남김.
  - `deliverables/…v19_목소리2_에코없음_상영용.mp4`: 울림 없음.
- 끝 타이틀 문구 "주민의 힘으로, 경상남도가 도약하다"는 **그대로 둡니다**(2026-11-02 확정).
- 에코는 v19의 두 버전 중 아직 고르지 않았습니다. 새 버전도 두 가지(줄임/없음)로 주거나, 확인 후 하나로 정합니다.
- 상영: 2026-11-12 10:00. 최종 검수 마감은 2026-11-06.

### v20 수정 요청 (2026-11-02, 반영 완료: 아래 "v20 반영 내용")

1. **초반 사람 AI 이미지 빼기.** 깔끔한 PPT 템플릿 같은 화면으로 바꿉니다.
   - 0~20초의 Grok 클립 3개를 뺍니다. 손에 바늘 꿰기(`v13_g1_hands.mp4`), 땀 한 방울 얼굴(`v14_face0.mp4`), 바느질(`v13_g3_stitch.mp4`)입니다.
   - 고칠 곳은 `scripts/build8.py`의 `vid('v1'…)`, `vid('v2'…)`, `vid('v3'…)` 세 줄과, `scripts/main5.js`의 "기" 부분(`#v1-w`~`#v3-w`)입니다.
   - 대신 HTML/CSS로 템플릿형 화면을 만듭니다. 예: 아이보리 바탕, 조각보 색 띠·도형, 함초롬바탕 제목과 키워드, 단정한 슬라이드 전환.
   - 이 구간 내레이션 L01·L02("새벽을 여는 손끝에서…", "이마에 맺힌 땀 한 방울은…")와 내용이 맞아야 합니다.
2. **음악을 더 빠르게.** 빠르게 해서 듣기 거북하면 다른 빠른 곡으로 바꿉니다.
   - 지금 곡은 `audio/bgm3.wav`(178초)이고, `mix9.py`가 이 파일을 읽습니다.
   - 템포만 올리면(예: `ffmpeg -af rubberband=tempo=1.12`) 곡이 짧아집니다. 반복·연장으로 178초를 채워야 합니다.
   - 지역 전환 간격(5.4초/5초)과 효과음 시각(`mix9.py`의 T)이 곡과 맞는지 다시 확인해야 합니다.
3. **내레이션을 더 빠르고 힘차게.**
   - Kanika로 다시 녹음합니다. 예: `python scripts/tts_kanika.py all fgh 1.05 0.3`. 인자는 줄, 녹음 이름(테이크), 속도, 안정도이며, 안정도를 낮추면 더 힘이 실립니다.
   - 녹음을 늘이거나 줄이는 처리는 하지 말고, 모델의 속도 설정(최대 1.2)으로만 조절합니다.
   - 녹음 뒤에는 `eval8.py` → `narr/v8/picks.json` 수정 → `prep_narr.py` → `build8.py` 순서로 진행합니다.
4. **끝 화면의 움직이는 AI 바다 화면 빼기.** 1번과 같은 템플릿 바탕으로 바꾸되, 문구·"2026년 제8회 경상남도 주민자치 박람회"·경남 로고는 그대로 둡니다.
   - 162.4~178초의 `vid('v9', 'v13_c9_islands.mp4'…)`를 뺍니다.
   - 지금 타이틀은 흰 글씨+그림자라 바다 위에서 읽힙니다. 밝은 바탕으로 바꾸면 글자색(`#fin2`, `#fin3`, `style5.css`)도 함께 바꿔야 합니다.

### v20 반영 내용 (2026-11-02)

1. **초반 0~19초 → 템플릿 슬라이드 3장.** Grok 클립 3개(`v13_g1_hands`, `v14_face0`, `v13_g3_stitch`)를 뺐습니다.
   - 아이보리 바탕, 위·아래 조각보 색 띠, 머리글("제8회 경상남도 주민자치 박람회", 쪽 번호 01~03/03)
   - 1장 "첫 땀 / 새벽을 여는 손끝에서"(L01), 2장 "땀 한 방울 / 우리 마을을 잇는 첫 바늘땀"(L02), 3장 "한 조각씩, 하나의 천으로 / 경상남도 18개 시군의 이야기"
   - 오른쪽 조각보가 장마다 세 조각씩 바느질되어 3장 끝에 9조각 정사각형이 되고, 19초 조각보 세상(승)으로 넘어갑니다.
   - 이 구간 자막(L01·L02)은 밝은 바탕용으로 진한 먹색+금색 강조, 어두운 자막 그라데이션 없음(`.ncap.lt`).
   - 코드: `build8.py`의 `TPL`, `QB`, `#s1`, `main5.js`의 "기" 부분, `style5.css` 끝의 v20 블록.
2. **음악 → `audio/bgm4_fast.wav`(약 1.15배, 116 → 약 133bpm).** `python scripts/music_fast.py`로 만듭니다.
   - bgm3를 장면 전환점(27.7 / 74.15 / 83.6 / 150초)에서 나누고, 구간마다 마디 몇 개를 한 번 반복한 뒤 rubberband로 빠르게 해서 원래 길이(178초)를 맞췄습니다. 그래서 큰 전환과 효과음 시각(`mix9.py`의 T)은 그대로 맞습니다. 74~83초 실 클로즈업의 조용한 구간은 원래 속도입니다.
   - `mix9.py` 다섯 번째 인자로 음악 파일을 고를 수 있습니다(기본값 `bgm4_fast.wav`, v19 음악은 `bgm3.wav`).
3. **내레이션 다시 녹음(테이크 f/g/h, L15는 j).** 고른 테이크: L01 h, L02 f, L03 f(h는 음악 속에서 "의령"이 "의룡"으로 들려 교체), L04 g, L05 g, L06 h(f는 음악 속에서 "가꾸고"가 "바꾸고"로 들려 교체), L07 g, L08 h, L09 f, L10 g, L11 g, L12 g, L13 g, L14 g, L15 j. `python scripts/tts_kanika.py all fgh 1.1 0.3 energetic`
   - **주의: eleven_v4는 speed 값을 무시합니다**(0.7과 1.2가 같은 길이). 그래서 v4의 연기 지시 태그 `[energetic]`와 stability 0.3으로 빠르고 힘차게 읽게 했습니다. v19보다 줄마다 8~15% 짧고, 태그는 소리 내어 읽지 않습니다(받아쓰기로 확인). 타임 스트레치는 하지 않았습니다.
   - L15(구호)는 태그를 붙이면 음이 너무 높아져서(소리 지르는 느낌) 태그 없이 stability 0.3으로 녹음한 j를 씁니다.
   - `narr/v8/picks.json`의 `kanika`가 v20 선택이고, v19 선택은 `kanika_v19`, v19 다듬은 녹음은 `narr/v8p/kanika_v19/`에 남겨 두었습니다.
   - 계정이 Starter 등급이라 192kbps가 안 돼서, `tts_kanika.py`가 자동으로 128kbps로 받습니다.
4. **끝 162.4~178초 → 같은 템플릿 바탕.** 섬 항공 클립(`v13_c9_islands`)과 빛번짐·플레어를 뺐습니다. 문구·"2026년 제8회 경상남도 주민자치 박람회"·경남 로고는 그대로이고, 글자색을 먹색/금색으로 바꿨습니다. 가운데에 18개 시군 이름 조각(2줄×9)이 한 조각씩 바느질되어 나타납니다.

## 2. 폴더 구성

| 경로 | 내용 |
|---|---|
| `video/` | HyperFrames 0.8.164 프로젝트. `index.html`이 영상 전체(빌드 결과물), `assets/`에 사진·영상 클립·소리·글꼴 |
| `scripts/build8.py` | `video/index.html`을 만드는 빌드 스크립트. 움직임은 `main5.js`, 스타일은 `style5.css`에 있고 빌드 때 HTML 안에 들어감 |
| `scripts/mix9.py` | 배경음악+내레이션+효과음을 섞어 최종 소리(wav)를 만듦 |
| `scripts/music_fast.py` | v20 빠른 배경음악 `audio/bgm4_fast.wav`를 bgm3에서 만듦 |
| `scripts/tts_kanika.py` | Kanika 목소리로 내레이션을 녹음함(본인 API 키 필요) |
| `scripts/prep_narr.py` | 고른 녹음본을 다듬어 `narr/v8p/kanika/`에 넣음 |
| `scripts/eval8.py`, `stt_check.py` | 녹음본 점수 매기기, 완성 소리 받아쓰기 검수 |
| `scripts/flicker.py` | 렌더본의 화면 튐(깜빡임) 검사 |
| `narr/script6.json` | 내레이션 15줄(시작 시각 `t`, 자막 문구 `text`, 녹음용 문구 `tts`) |
| `narr/caplines6.json` | 자막 줄바꿈·단위·강조. `[ ]` 안은 금색 강조 |
| `narr/v8/kanika/*.mp3` | Kanika 녹음 원본(줄마다 여러 개). `narr/v8/picks.json`이 고른 것 |
| `narr/v8p/kanika/*.wav` | 실제로 쓰는 다듬은 녹음. `bomi/`는 1번 목소리이며, 빌드의 자막 시간 계산에만 쓰임 |
| `audio/bgm3.wav` | 배경음악(178초). `master_mix9_less.wav`·`master_mix9_dry.wav`는 v19 최종 소리 |
| `sfx/` | 효과음(쿵·휙·반짝) |
| `photos.json` | 18개 시군 × 사진 3장 + 사진 설명 문구 |
| `prompts/` | 영상 클립·이미지를 만들 때 쓴 프롬프트. `v13/`은 지금 쓰는 클립용, `v18/`은 AI 사진 6장용 |
| `gen/v13/*.png` | Grok 영상 클립의 시작 이미지 |
| `ref/` | 최신 내레이션 원고(hwpx·텍스트), 마지막 사진 원본 3장, AI 사진 6장 |
| `deliverables/` | v19 상영용 두 가지 |
| `fonts_dl/` | 글꼴. 함초롬바탕은 받아서 넣어야 함(`fonts_dl/README.txt`) |

## 3. 작업 환경 (Windows 기준)

1. Node.js 18 이상. HyperFrames는 `npx --yes hyperframes@0.8.164 …`로 실행되며 따로 설치할 필요가 없습니다.
2. ffmpeg / ffprobe가 PATH에 있어야 합니다.
3. Python 3.11 이상: `pip install numpy scipy librosa pillow fonttools brotli faster-whisper`
   - faster-whisper는 처음 실행할 때 medium 모델(약 1.5GB)을 받습니다.
4. 함초롬바탕 글꼴: `fonts_dl/README.txt`대로 한컴 공식 파일을 받아 `fonts_dl/HCRBatang.ttf`, `HCRBatang-Bold.ttf`를 넣습니다.
5. `python scripts/build8.py`를 한 번 실행합니다. 이때 제목용 글꼴 조각(woff2)이 만들어집니다.

스크립트는 자기 위치를 기준으로 경로를 찾으므로 폴더를 어디에 풀어도 됩니다.

## 4. 작업 순서와 명령

```bash
# (1) 화면 빌드: 문구·자막·사진·타이밍을 바꾼 뒤
python scripts/build8.py

# (2) 확인 (빠름)
cd video
npx --yes hyperframes@0.8.164 lint
npx --yes hyperframes@0.8.164 snapshot --at 4,35,136,152,166.5 -o ../snap --no-end --timeout 60000
# ../snap/contact-sheet.jpg 를 열어 확인

# (3) 렌더: 약 8분
npx --yes hyperframes@0.8.164 render -f 30 -q delivery -o renders/jumin-expo-vNN.mp4 --browser-timeout 180
cd ..

# (4) 소리 섞기
python scripts/mix9.py kanika less -26 0.4   # 에코 줄임 -> audio/master_mix9_less.wav
python scripts/mix9.py kanika dry off        # 에코 없음 -> audio/master_mix9_dry.wav
# 인자: 목소리 / 결과 이름 / 울림 크기(dB, off=없음) / 울림 길이(초)

# (5) 영상+소리 합치기 (상영용, 미리보기)
ffmpeg -y -i video/renders/jumin-expo-vNN.mp4 -i audio/master_mix9_less.wav -map 0:v -map 1:a -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 320k -t 178 deliver_vNN.mp4
ffmpeg -y -i deliver_vNN.mp4 -c:v libx264 -b:v 8M -maxrate 10M -bufsize 16M -preset medium -c:a aac -b:a 192k -movflags +faststart preview_vNN.mp4

# (6) 검수
python scripts/flicker.py deliver_vNN.mp4        # 19.00초 한 번은 원래 있는 빛번짐 전환이라 정상
python scripts/stt_check.py audio/master_mix9_less.wav
```

**소리만 바꿀 때는 렌더가 필요 없습니다.** 기존 상영용 영상의 화면만 그대로 가져다 붙이면 됩니다.

```bash
ffmpeg -y -i "deliverables/주민자치박람회_주제영상_v19_목소리2_에코없음_상영용.mp4" -i audio/master_mix9_xxx.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -movflags +faststart -t 178 out.mp4
```

## 5. 내레이션을 다시 녹음할 때

```bash
set ELEVENLABS_API_KEY=본인키      # PowerShell은  $env:ELEVENLABS_API_KEY="본인키"
python scripts/tts_kanika.py L05 abc        # 바꾼 줄만, 3번씩
python scripts/eval8.py kanika              # 점수표 narr/v8/kanika_eval.txt + 추천 narr/v8/kanika_pick_auto.json
# narr/v8/picks.json 의 "kanika" 항목에서 쓸 녹음 글자(a, b, c …)를 고친 뒤
python scripts/prep_narr.py                 # narr/v8p/kanika/*.wav 갱신, 다음 줄과 겹치는지 출력
python scripts/build8.py                    # 자막 시간도 새 길이에 맞춤 → 렌더 → 믹스
```

- 문구를 바꾸면 `narr/script6.json`의 `text`(자막)와 `caplines6.json`(자막 줄바꿈)을 같이 고칩니다. 소리 내어 읽는 문구가 달라야 하면 `tts`를 씁니다(예: "18개" → "열여덟 개").
- 녹음 설정: eleven_v4, stability 0.4, similarity 0.75, speed 0.88(v19 기준). 너무 빠른 줄은 0.82로 다시 녹음합니다. 쉼표는 "..."로 바꿔 보내서 숨을 쉬게 합니다.
- `tts_kanika.py`의 세 번째 인자는 속도, 네 번째는 stability입니다. 11-02 요청("더 빠르고 힘차게")에는 속도 1.0~1.1, stability 0.3 정도부터 시험해 보세요.
- **하지 말 것**
  - 녹음을 늘려서 느리게 만들기(타임 스트레치). 기계적으로 들린다는 지적을 받았습니다.
  - multilingual_v2 모델. "손끝"을 "송곳"처럼 읽습니다.
  - "!"를 그대로 보내기. 소리를 질러서, 마지막 줄은 ", ."로 읽힙니다(`tts_kanika.py`의 CALM).
- 받아쓰기 검수에서 '첫담', '바꾭니다', '하만', '18'로 나오는 건 표기 차이일 뿐 오류가 아닙니다.

## 6. 타임라인 (scripts/build8.py 의 T)

| 초 | 장면 |
|---|---|
| 0–19 | 기: 템플릿 슬라이드 3장(v20). v19까지는 바늘에 실 꿰는 손 → 땀 한 방울 얼굴 → 바느질(Grok 클립 3개) |
| 19–75 | 승: 조각보 위 1~9번 시군(창원~의령). 23.4초부터 5.4초 간격. 70초에 위쪽 절반 전체 보기 |
| 74.6–84 | 실 클로즈업 클립 |
| 83.3–140 | 전: 10~18번 시군(함안~합천). 86.6초부터 5초 간격. 131초에 18조각 전체가 하나의 천 |
| 139.2 | 결: 천을 하늘로 던지는 클립 |
| 149.6–162 | 마지막 사진 3장(의령 → 창원 → 밀양, 4.6초 간격) |
| 162.4–178 | 템플릿 바탕 위 타이틀 + "2026년 제8회 경상남도 주민자치 박람회" + 18개 시군 조각 + 경남 로고(v20). 마지막 3초 페이드 |

내레이션 15줄의 시작 시각은 `narr/script6.json`의 `t`이고, 원고의 타임코드와 같습니다.
15번(마지막 줄)은 타이틀과 겹쳐서 자막을 넣지 않습니다(`build8.py`에서 L15를 뺌).

## 7. 정해진 규칙 (리뷰 이력에서 확정된 것)

- 글꼴: 제목·지역 이름표는 **함초롬바탕**, 자막·사진 설명은 **Pretendard** SemiBold/Bold.
- 자막
  - 따뜻한 흰색에, 강조는 차분한 금색입니다.
  - 최대 2줄이고, 아래쪽 8% 안전 영역 안에 둡니다.
  - 단위별로 0.3초 간격으로 20px 아래에서 0.6초 동안 떠오르고, 0.5초 동안 사라집니다.
  - 회전·튀기·번쩍임은 넣지 않습니다. **검은 자막 배경 상자도 넣지 않습니다.**
- 사진마다 아래에 설명 칸이 있습니다(`photos.json`의 cap).
- **사진은 크게 보이게** 합니다. 화면을 줄여 자막 자리를 만든 버전은 거절됐습니다.
- 땀 표현은 이마 가운데 한 방울이 천천히 코 중간까지 내려오는 정도입니다(v15).
- 배경음악은 웅장하게 둡니다. 대신 내레이션이 묻히지 않도록, 음악의 목소리 대역(300~4000Hz)만 말하는 동안 낮춥니다(`mix9.py`의 carve). 최종 음량은 −14 LUFS 근처입니다.
- 최신 원고(`ref/내레이션원고_최신…`)의 10번 오타 "인사과"는 "인사와"로 반영했습니다.
- 영상 클립을 새로 만들 때는 Grok Imagine을 쓰고(이미지 → 영상, 720p까지), 1080p로 키워서 넣습니다. 프롬프트는 `prompts/v13/`에 있습니다.
- 정지 이미지는 이미지 생성 도구로 만듭니다. AI 사진 6장의 프롬프트는 `prompts/v18/`에 있습니다.
- 최종본은 늘 두 파일로 만듭니다. 상영용(crf 17, 약 360MB)과 미리보기(8Mbps, 약 180MB)입니다.

## 8. 버전 흐름 요약

- v1~v15: 기획안대로 구성한 뒤 피드백을 반영했습니다. 함초롬바탕, 화려한 연출·조명, 지역 이동 속도, 검은 자막 배경 제거와 사진 설명 칸, 경남 로고, 끝 문구 "2026년 제8회 경상남도 주민자치 박람회", 자막 규격(v10), 땀 표현(v15).
- v16: 한글 원고 15줄 반영, 30대 여성 목소리. 목소리를 늘려 느리게 했는데 기계적이라는 평을 받았습니다.
- v17: 더 나이 든 목소리(Jian.K)로 바꾸고 사진 크기를 원래대로 되돌렸습니다.
- v18: 새 원고 `내레이션(1).hwpx` 반영, 지정 목소리 2개로 2편, 마지막 사진 교체, AI 사진 6장.
- v19: 목소리 2번(Kanika) 확정. 에코 줄임 / 에코 없음 두 가지.
- v20: 11-02 요청 4가지 반영. 초반·끝 AI 화면을 템플릿으로 교체, 음악(bgm4_fast)·내레이션([energetic] 재녹음)을 더 빠르게. 1장 참고.
