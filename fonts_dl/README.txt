글꼴 안내

1) Pretendard (자막용) - pre/ 폴더에 들어 있음. SIL Open Font License 1.1 (pre/LICENSE.txt).

2) 함초롬바탕 (제목·지역 이름표용) - 한컴 글꼴이라 파일을 같이 보내지 않았습니다(영상 사용은 가능, 글꼴 파일 재배포는 불가).
   한컴 공식 배포본을 받아서 이 폴더에 아래 두 파일을 넣으세요.
     fonts_dl/HCRBatang.ttf
     fonts_dl/HCRBatang-Bold.ttf

   받는 방법 (Referer가 없으면 거부됨):
     curl -L -e https://www.hancom.com/ -o fonts_dl/HancomFont.zip https://cdn.hancom.com/pds/docs/HancomFont.zip
   zip 안의 HCRBatang.ttf, HCRBatang-Bold.ttf를 fonts_dl/ 에 풀면 됩니다.

   그다음 python scripts/build8.py 를 실행하면 영상에 쓰는 글자만 골라
   video/assets/fonts/hcr-batang.woff2, hcr-batang-bold.woff2 를 새로 만듭니다.
   (이 두 파일이 없으면 제목 글씨가 다른 글꼴로 나옵니다.)
