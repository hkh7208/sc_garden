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
- MARIADB_HOST (기본: 127.0.0.1)
- MARIADB_PORT (기본: 3306)

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
G:/VS_code/sc_garden/.venv/Scripts/python.exe manage.py runserver
```

## Tailwind CSS
템플릿에서 CDN 방식으로 Tailwind CSS를 사용합니다. 필요 시 빌드 방식으로 전환 가능합니다.
