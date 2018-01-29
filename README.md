# Web-screenshot

>BoB 6th Digital Forensics
  <br>최정완


## Requirements

- OS: Linux(ubuntu)
- python2
- PyQt4
- python-piexif
- python-pillow


## Usage

- python web_screenshot.py
- Full: Capture Full Screenshot of current web page
- Part: Capture Part of current web page
- Script: Save the script of current web page

## Description

1. 프로그램을 실행하고 원하는 사이트에 접속합니다.
2. 채증하고자 하는 사이트에 접속한 후, 캡처 기능을 사용합니다.
3. 페이지 전체 스크린샷을 원할 경우 Full 버튼
4. 현재 보이는 화면에 대한 스크린샷을 원할 경우 Current 버튼
5. 페이지의 소스코드를 원할 경우 Script 버튼
6. 직전 페이지로 돌아가고 싶은 경우 Back 버튼
7. 캡처된 결과물(사진파일, html파일)은 현 폴더 내에 생성되는 export 폴더에 저장됩니다.
8. export 폴더 안에 있는 capture.db 에는 채증한 파일들에 대한 간단한 정보가 저장됩니다.

