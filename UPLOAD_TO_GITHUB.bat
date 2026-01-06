@echo off
chcp 65001 > nul
echo.
echo ============================================
echo   Freediving Safety Simulator GitHub Upload
echo ============================================
echo.

:: 현재 폴더로 이동
cd /d "%~dp0"

:: Git 확인
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Git이 설치되어 있지 않습니다!
    echo Git 설치: https://git-scm.com/download/win
    pause
    exit /b 1
)

:: Git 사용자 설정 (없으면 설정)
git config user.name >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [설정] Git 사용자 이름 설정 중...
    git config --global user.name "Ftoaster"
)

git config user.email >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [설정] Git 이메일 설정 중...
    git config --global user.email "ftoaster@users.noreply.github.com"
)

:: 기존 .git 폴더 삭제 (문제가 있을 수 있으므로 새로 시작)
if exist ".git" (
    echo [정리] 기존 Git 설정 제거 중...
    rmdir /s /q ".git"
)

:: Git 초기화
echo [1/5] Git 저장소 초기화 중...
git init

:: 브랜치 이름을 main으로 설정
git branch -M main

:: 파일 추가
echo [2/5] 파일 추가 중...
git add index.html
git add manifest.json
git add sw.js
git add README.md
git add .gitignore

:: 상태 확인
echo.
echo [확인] 추가된 파일:
git status --short

:: 커밋
echo.
echo [3/5] 커밋 중...
git commit -m "Freediving Safety Simulator PWA"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] 커밋 실패! 파일이 제대로 추가되었는지 확인하세요.
    pause
    exit /b 1
)

:: Remote 추가
echo.
echo [4/5] GitHub 연결 중...
git remote remove origin 2>nul
git remote add origin https://github.com/Ftoaster/freediving-safety-sim.git

:: 푸시
echo.
echo [5/5] 업로드 중...
git push -u origin main --force

echo.
if %ERRORLEVEL% EQU 0 (
    echo ============================================
    echo   업로드 완료!
    echo ============================================
    echo.
    echo 이제 GitHub Pages를 활성화하세요:
    echo.
    echo 1. 아래 링크 접속:
    echo    https://github.com/Ftoaster/freediving-safety-sim/settings/pages
    echo.
    echo 2. Source: Deploy from a branch
    echo 3. Branch: main / root 선택
    echo 4. Save 클릭
    echo.
    echo 앱 주소: https://ftoaster.github.io/freediving-safety-sim/
) else (
    echo.
    echo [ERROR] 업로드 실패!
    echo.
    echo 해결 방법:
    echo 1. GitHub 로그인 창이 뜨면 로그인하세요
    echo 2. 다시 이 파일을 실행하세요
)

echo.
pause
