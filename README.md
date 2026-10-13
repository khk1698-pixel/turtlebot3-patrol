[README.md](https://github.com/user-attachments/files/33374458/README.md)
# ROS 2 TurtleBot3 자율주행 순찰 시스템

WSL2(Ubuntu 24.04)의 ROS 2 Jazzy 환경에서 TurtleBot3를 Gazebo로 시뮬레이션하고, **SLAM으로 지도를 만든 뒤 Nav2 자율주행**과 **Python 순찰 노드**로 지정한 지점들을 무한 반복 순찰하는 프로젝트입니다. 실물 로봇 없이 시뮬레이션만으로 지도 작성부터 자율주행, 순찰 제어까지 전체 과정을 구현했습니다.

<!-- 순찰하는 모습을 녹화해 docs/images/patrol_demo.gif 로 저장한 뒤, 아래 줄의 주석을 해제하세요. -->
<!-- ![순찰 데모](docs/images/patrol_demo.gif) -->

![Gazebo 시뮬레이션 화면](docs/images/gazebo_view.png)

## 주요 기능

- **SLAM 지도 작성**: 라이다 데이터로 환경 지도를 만들어 `map.pgm`, `map.yaml`로 저장
- **지도 기반 자율주행**: 저장한 지도로 Nav2를 실행해 목표 지점까지 경로 계획 및 이동
- **무한 반복 순찰**: 지정한 3개 지점을 순서대로 돌고, 한 바퀴가 끝나면 다시 반복
- **지점별 대기**: 지점에 도착하면 설정한 시간(기본 3초) 동안 정지
- **이동 기록**: 바퀴 수, 지점, 성공/실패를 시간과 함께 터미널과 로그 파일에 기록
- **안전한 중단**: `Ctrl+C` 입력 시 진행 중인 이동을 취소하고 종료

## 개발 환경

| 구분 | 내용 |
|---|---|
| 운영체제 | Windows PC의 WSL2, Ubuntu 24.04 |
| ROS | ROS 2 Jazzy |
| 시뮬레이터 / 시각화 | Gazebo Sim, RViz2 |
| 로봇 모델 | TurtleBot3 `waffle` |
| SLAM / 내비게이션 | Cartographer, Nav2 |
| 제어 | Python, `nav2_simple_commander` |

## 시스템 구성

![시스템 구성도](docs/images/flow_diagram.png)

1. Gazebo에서 TurtleBot3가 라이다 데이터(`/scan`)를 발행합니다.
2. Cartographer가 로봇을 움직이며 모은 데이터로 지도를 만들고 파일로 저장합니다.
3. Nav2가 저장된 지도 위에서 경로를 계획하고 이동 명령(`/cmd_vel`)을 보냅니다.
4. `patrol.py`가 `BasicNavigator`로 목표 지점을 Nav2에 차례로 전달합니다.
5. 도착과 실패 결과를 대기 시간과 함께 로그로 남깁니다.

## 저장소 구조

```
ros2-turtlebot3-patrol/
├─ README.md
├─ scripts/
│  └─ patrol.py             # 순찰 노드
├─ maps/
│  ├─ map.pgm               # SLAM으로 만든 지도 이미지
│  └─ map.yaml              # 지도 설정
├─ docs/images/             # 실행 화면, 구성도
└─ logs/
   └─ sample_patrol_log.txt # 실행 로그 예시
```

## 설치

Ubuntu 24.04 기준입니다. 다른 버전에서는 ROS 2 배포판 이름이 달라집니다(예: 22.04는 Humble).

**1. ROS 2 apt 저장소 등록**

```bash
sudo apt install software-properties-common curl -y
sudo add-apt-repository universe
sudo apt update

export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
```

**2. ROS 2 Jazzy 설치**

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install ros-jazzy-desktop -y
```

**3. 프로젝트 패키지 설치**

```bash
sudo apt install -y \
  ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
  ros-jazzy-nav2-simple-commander \
  ros-jazzy-turtlebot3-gazebo ros-jazzy-turtlebot3-teleop \
  ros-jazzy-turtlebot3-navigation2 ros-jazzy-turtlebot3-cartographer
```

**4. 환경 설정**

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
echo "export TURTLEBOT3_MODEL=waffle" >> ~/.bashrc
source ~/.bashrc
```

설치가 끝나면 `ros2 --help`로 설치를 확인할 수 있습니다. WSL2에서 Gazebo와 RViz2 창을 띄우려면 GUI 지원(WSLg)이 동작해야 합니다.

## 실행 방법

### 1. 순찰 실행 (저장소의 지도 사용)

저장소 루트에서 터미널 3개를 사용합니다.

```bash
# 터미널 A: Gazebo 월드
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# 터미널 B: Nav2 (저장소의 지도 사용)
ros2 launch turtlebot3_navigation2 navigation2.launch.py use_sim_time:=True map:=$PWD/maps/map.yaml

# 터미널 C: 순찰 노드
python3 scripts/patrol.py
```

Nav2가 완전히 준비된 뒤(RViz2에 지도가 보이는 상태) 터미널 C를 실행하세요. 순찰을 멈추려면 `Ctrl+C`를 누릅니다.

### 2. 지도를 직접 만들려면 (SLAM)

```bash
# 터미널 A: Gazebo 월드
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# 터미널 B: Cartographer SLAM
ros2 launch turtlebot3_cartographer cartographer.launch.py use_sim_time:=True

# 터미널 C: 키보드로 로봇을 천천히 움직이며 지도 작성
ros2 run turtlebot3_teleop teleop_keyboard

# 지도가 충분히 그려지면 저장 (홈 폴더에 map.pgm, map.yaml 생성)
ros2 run nav2_map_server map_saver_cli -f ~/map
```

## 순찰 노드 (`scripts/patrol.py`)

파일 상단의 설정만 바꾸면 동작을 조절할 수 있습니다.

| 설정 | 설명 |
|---|---|
| `POINTS` | 순찰 지점 좌표 목록 (지도 기준) |
| `WAIT_SEC` | 지점 도착 후 대기 시간(초) |
| `SET_INITIAL_POSE` | 시작 시 초기 위치(0, 0)를 설정할지 여부 |
| `LOG_FILE` | 로그 저장 위치 (기본 `~/patrol_log.txt`) |

**순찰 지점 좌표 얻기**: RViz2에서 **Publish Point**로 지도를 클릭한 뒤 `ros2 topic echo /clicked_point`로 확인합니다. 좌표는 Gazebo가 아니라 지도(`map`) 기준입니다.

**초기 위치**: `SET_INITIAL_POSE = True`는 로봇이 처음 출발한 자리에 있을 때만 사용합니다. 순찰을 중단했다가 다시 실행할 때는 `False`로 바꿔야 위치가 어긋나지 않습니다.

**설계 포인트**
- 지점마다 대기해야 해서 `followWaypoints` 대신 `goToPose`로 지점을 하나씩 보내는 방식을 택했습니다.
- 이동에 실패한 지점은 건너뛰고 다음 지점으로 진행해 순찰이 멈추지 않게 했습니다.
- 모든 동작을 터미널과 파일에 동시에 기록하고, `Ctrl+C`는 `cancelTask`로 진행 중인 이동을 취소한 뒤 종료합니다.

로그는 아래와 같은 형식으로 기록됩니다.

```
[2026-10-13 14:02:11] 순찰 시작 (중단하려면 Ctrl+C)
[2026-10-13 14:02:11] --- 1번째 바퀴 시작 ---
[2026-10-13 14:02:11] [1바퀴] 1/3번째 지점 (1.62, 1.8)로 이동 시작
[2026-10-13 14:02:58] [1바퀴] 1번째 지점 도착, 3초 대기
```

## 트러블슈팅

| 증상 | 원인과 해결 |
|---|---|
| `/opt/ros/jazzy/setup.bash: No such file or directory`, `ros2: command not found` | ROS 2 apt 저장소를 등록하지 않아 설치가 진행되지 않은 상태입니다. 저장소를 등록한 뒤 `ros-jazzy-desktop`을 설치합니다. |
| `Package 'turtlebot3_teleop' not found` | 별도 패키지입니다. `ros-jazzy-turtlebot3-teleop`을 설치합니다. |
| RViz2의 Publish Point 좌표가 출력되지 않음 | 진행 중이던 Nav2 목표를 먼저 취소하고, `ros2 topic echo /clicked_point`를 켜 둔 뒤 지점마다 Publish Point를 다시 선택해 클릭합니다. |
| 재실행 시 로봇이 엉뚱하게 이동 | 로봇이 시작 위치에 있지 않은데 초기 위치가 (0, 0)으로 설정된 경우입니다. `SET_INITIAL_POSE = False`로 바꿉니다. |
| 시뮬레이션이 실제 시간보다 느림 | WSL2 환경의 성능 한계입니다. 실행에는 문제가 없습니다. |

## 한계와 향후 계획

- 순찰 지점이 코드 안에 고정되어 있어, 별도 설정 파일(YAML)로 분리할 예정입니다.
- 터미널 3개로 나눠 실행하는 과정을 launch 파일 하나로 합칠 수 있습니다.
- 월드에 장애물을 추가해 회피 성능을 확인하고, 이동 속도 파라미터에 따른 결과를 비교해 볼 수 있습니다.
- 여러 PC를 네트워크로 연결해 원격으로 실행하고 조종하는 구성을 시도할 계획입니다.
- 실물 TurtleBot3 같은 로봇에 같은 코드를 이식해 볼 수 있습니다.
