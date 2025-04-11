# TNFSH Scoreboard

## About
學校的成績系統界面對手機使用者不太友善，需要多次點擊與頁面縮放，因此這個項目就誕生了

## Project Structure
基本上是參考 [TOJ](https://github.com/Tfcis/NTOJ) 的架構

| Codebase                   |         Description          |
|:---------------------------|:----------------------------:|
| [Api](src/services/api.py) | API Client for school system |
| [Backend](src/)            |       Tornado backend        |
| [Frontend](src/static/)    |     Bootstrap5 frontend      |

## Contribute
先到Issues提Bug或Feature，之後在PR上指向之前發的Issue

## Prerequisites

Before you begin, make sure you have the following installed:
- Python (version 3.11 or higher)
- Poetry (recommended)
- or pip

## Installation

### Using Poetry (recommended)

1. Clone the repository:
    ```shell
    git clone https://github.com/tobiichi3227/TNFSH-Scoreboard.git
    cd TNFSH-Scoreboard
    ```
2. Install dependencies:
    ```shell
    poetry install
    ```
3. Activate the virtual environment:
    ```shell
    poetry env activate
    poetry shell
    ```

### Using pip

1. Clone the repository:
    ```shell
    git clone https://github.com/tobiichi3227/TNFSH-Scoreboard.git
    cd TNFSH-Scoreboard
    ```
2. Create and activate a virtual environment:
    ```shell
    python -m venv venv
    source venv/bin/activate # On Windows use `venv\Scripts\activate`
    ```
3. Install dependencies:
    ```shell
    pip install -r requirements.txt
    ```

## Usage
Run server

```
python src/server.py
```

## Configuration

To configure the application, update the `config.py` file in the `src/config` directory. Key parameters include:
```
MAIN_URL = 'https://hschool-mlife.k12ea.gov.tw/ecampus_KH'
SCHNO = '210305D'
PORT = 5227
SECRET_COOKIE = 'tobiichi3227orzorz'
BASE_URL = '/'
```

- `MAIN_URL`: 校務系統的網址
- `SCHNO`: 校務系統網址中的學校ID
    `https://epf.mlife.com.tw/ecampus_KH/Login.action?schNo=210305D`，這邊的 `schNo=210305D` 即是
- `PORT`: 服務使用的端口
- `SECRET_COOKIE`: 服務用於加密 cookie 的(建議長度大於32位的隨機字串)
- `BASE_URL`: 服務網址，如果使用如 `/board` 之類的，要搭配 `nginx` 等 Reserve Proxy Server

### Nginx Configuration
```nginx
location /board/ {
    rewrite ^/board/(.*) /$1 break;
    proxy_pass http://localhost:PORT;
    proxy_read_timeout 14400s;
    proxy_http_version 1.1;
}
```

## License

This project is licensed under the GNU General Public License v2.0 (GPL-2.0).
See the [LICENSE](./LICENSE) for more information.
