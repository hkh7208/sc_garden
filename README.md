# SC Garden Portfolio

## 개요
순천만 정원의 사진 포트폴리오 사이트입니다. Django + MariaDB + Tailwind CSS를 사용합니다.

## 사전 준비
- MariaDB 서버 실행
- 데이터베이스 및 사용자 생성

예시 SQL:
```
CREATE DATABASE sc_garden CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sc_garden_user'@'localhost' IDENTIFIED BY 'sc_garden_password';
GRANT ALL PRIVILEGES ON sc_garden.* TO 'sc_garden_user'@'localhost';
FLUSH PRIVILEGES;
```

## 환경 변수
다음 환경 변수를 필요에 따라 변경하세요:
- MARIADB_NAME (기본: sc_garden)
- MARIADB_USER (기본: sc_garden_user)
- MARIADB_PASSWORD (기본: sc_garden_password)
- MARIADB_HOST (설정 시 강제 우선, 미설정 시 자동 라우팅)
- MARIADB_PORT (기본: 3306)
- MARIADB_LOCAL_HOST (기본: 192.168.0.107)
- MARIADB_NAS_HOST (기본: 192.168.0.250)
- SERVER_PROFILE (`local` 또는 `nas`, 미설정 시 자동 감지)
- NAS_SERVER_IP (기본: 192.168.0.250)
- NAS_RUNTIME_MARKERS (기본: `/volume1,/var/services`, 해당 경로 존재 시 nas로 판단)

환경 파일 템플릿:
- 로컬 개발: `.env.local.example` → `.env`로 복사
- NAS 배포: `.env.nas.example` → `.env`로 복사

## 설치
```
G:/VS_code/sc_garden/.venv/Scripts/python.exe -m pip install -r requirements.txt
```

## 마이그레이션
```
G:/VS_code/sc_garden/.venv/Scripts/python.exe manage.py makemigrations
G:/VS_code/sc_garden/.venv/Scripts/python.exe manage.py migrate
```

## 기본 데이터 생성
```
G:/VS_code/sc_garden/.venv/Scripts/python.exe manage.py seed_portfolio
```

## 관리자 계정
```
G:/VS_code/sc_garden/.venv/Scripts/python.exe manage.py createsuperuser
```

## 실행
```
G:/VS_code/sc_garden/.venv/Scripts/python.exe manage.py run_auto_server
```

로컬 서버를 8080으로 고정 실행:
```
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_8080.ps1
```

## NAS 데이터 동기화(로컬 작업용)
NAS(192.168.0.250)의 DB와 `media`를 로컬로 가져올 때 사용합니다.

```
powershell -ExecutionPolicy Bypass -File .\scripts\sync_from_nas.ps1
```

옵션:
- `-SkipMedia`: DB만 동기화
- `-NasIp <IP>`: NAS IP 변경 시
- `-NasMediaShare <share path>`: 기본값 `web\sc_garden\media`

동기화 시 `backups/`에 다음 파일이 자동 생성됩니다.
- 로컬 DB 백업(`local_before_sync_*.json`)
- NAS 앱데이터 덤프(`nas_appdata_*.json`)

자동 실행 규칙:
- 로컬 개발 PC(기본): `127.0.0.1:8000` + local DB(`192.168.0.107`)
- NAS 서버 IP가 `192.168.0.250`인 환경: `0.0.0.0:8080` + nas DB(`192.168.0.250`)
- GitHub 동기화 후에도 동일 명령(`run_auto_server`)으로 자동 적용

자동 감지가 애매한 환경(컨테이너 등)에서는 NAS 서버의 `.env`에 아래처럼 고정하세요:
```
SERVER_PROFILE=nas
```

기존 공용 이미지 경로 이관(최초 1회 권장):
```
# 1) 로컬 DB 기준 변경 대상 확인
G:/VS_code/sc_garden/.venv/Scripts/python.exe manage.py migrate_photo_storage_paths --target local

# 2) 로컬 DB 실제 반영
G:/VS_code/sc_garden/.venv/Scripts/python.exe manage.py migrate_photo_storage_paths --target local --commit

# 3) NAS 서버에서도 동일하게(target만 nas)
python manage.py migrate_photo_storage_paths --target nas
python manage.py migrate_photo_storage_paths --target nas --commit
```

## Tailwind CSS
템플릿에서 CDN 방식으로 Tailwind CSS를 사용합니다. 필요 시 빌드 방식으로 전환 가능합니다.

## GitHub Self-hosted Runner 오류 복구
다음 오류가 보이면 이미 등록된 runner에 다시 `config`를 실행한 상태입니다.
- `Cannot configure the runner because it is already configured.`
- `Value cannot be null. (Parameter 'configuredSettings')`

설치경로 빠른 확인:

Windows (PowerShell, 서비스형 runner):
```
Get-CimInstance Win32_Service | ? Name -like 'actions.runner*' | select Name,State,PathName
```

Windows (폴더 스캔):
```
Get-ChildItem C:\,D:\,G:\ -Recurse -Filter config.cmd -ErrorAction SilentlyContinue | ? FullName -match 'actions-runner|runner' | select -Expand FullName
```

Linux/Synology:
```
find / -name config.sh 2>/dev/null
```

복구 순서(Windows runner):
```
cd <runner_설치_경로>
.\svc.cmd stop
.\svc.cmd uninstall
.\config.cmd remove
```

`remove`가 실패하면(설정 파일 손상):
```
cd <runner_설치_경로>
del .runner
del .credentials
del .credentials_rsaparams
del .service
```
그 다음 다시 등록:
```
.\config.cmd --url https://github.com/<owner>/<repo> --token <new_token>
.\svc.cmd install
.\svc.cmd start
```

복구 순서(Linux/Synology runner):
```
cd <runner_설치_경로>
./svc.sh stop
./svc.sh uninstall
./config.sh remove
```

`remove`가 실패하면:
```
cd <runner_설치_경로>
rm -f .runner .credentials .credentials_rsaparams .service
```
그 다음 다시 등록:
```
./config.sh --url https://github.com/<owner>/<repo> --token <new_token>
./svc.sh install
./svc.sh start
```
