from typing import Dict, List, ClassVar


hcs_client_version: ClassVar[str] = "1.8.9"

school_areas: Dict[str, List[str]] = {
    "area01": ["서울", "서울시", "서울교육청", "서울시교육청", "서울특별시", "서울특별시교육청"],
    "area02": ["부산", "부산광역시", "부산시", "부산교육청", "부산광역시교육청"],
    "area03": ["대구", "대구광역시", "대구시", "대구교육청", "대구광역시교육청"],
    "area04": ["인천", "인천광역시", "인천시", "인천교육청", "인천광역시교육청"],
    "area05": ["광주", "광주광역시", "광주시", "광주교육청", "광주광역시교육청"],
    "area06": ["대전", "대전광역시", "대전시", "대전교육청", "대전광역시교육청"],
    "area07": ["울산", "울산광역시", "울산시", "울산교육청", "울산광역시교육청"],
    "area08": ["세종", "세종특별시", "세종시", "세종교육청", "세종특별자치시", "세종특별자치시교육청"],
    "area10": ["경기", "경기도", "경기교육청", "경기도교육청"],
    "area11": ["강원", "강원도", "강원교육청", "강원도교육청"],
    "area12": ["충북", "충청북도", "충북교육청", "충청북도교육청"],
    "area13": ["충남", "충청남도", "충남교육청", "충청남도교육청"],
    "area14": ["전북", "전라북도", "전북교육청", "전라북도교육청"],
    "area15": ["전남", "전라남도", "전남교육청", "전라남도교육청"],
    "area16": ["경북", "경상북도", "경북교육청", "경상북도교육청"],
    "area17": ["경남", "경상남도", "경남교육청", "경상남도교육청"],
    "area18": ["제주", "제주도", "제주특별자치시", "제주교육청", "제주도교육청", "제주특별자치시교육청", "제주특별자치도"],
}


school_levels: Dict[str, List[str]] = {
    "level1": ["유치원", "유", "유치"],
    "level2": ["초등학교", "초", "초등"],
    "level3": ["중학교", "중", "중등"],
    "level4": ["고등학교", "고", "고등"],
    "level5": ["특수학교", "특", "특수", "특별"],
}

login_level: Dict[str, List[str]] = {
    "school": [
        "유치원",
        "유",
        "유치",
        "초등학교",
        "초",
        "초등",
        "중학교",
        "중",
        "중등",
        "고등학교",
        "고",
        "고등",
        "특수학교",
        "특",
        "특수",
        "특별",
    ],
    "univ": ["대학교", "대"],
    "office": ["교육행정", "교육행정기관", "행정기관", "학원"],
}

covid_19_guidelines = """
코로나19 예방 방역수칙 [교육부]

✅ 3밀(밀폐, 밀집, 밀접) 환경에서 마스크 KF80 이상 착용
✅ 30초 이상 비누로 손 씻기
✅ 상시 환기하기
✅ 기침할 때는 옷소매로 가리기
✅ 사적모임을 자제하고 대면 접촉 줄이기
✅ 아프면 검사하고 집에 머무르기
"""

covid_self_test_guide_youtubeURL = "https://www.youtube.com/watch?v=nv7tR1jsGzs"
