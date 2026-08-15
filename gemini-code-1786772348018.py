import streamlit as st
import re

# ==========================================
# 1. 자동 채점 로직 (Rule Engine)
# ==========================================

def grade_set1_q1(ans_a, ans_b, ans_c):
    """실전 적용-1 [서·논술형 1] 채점"""
    score = 0
    feedback = []

    # ㉠ 검증: 난이도가 낮음 / 쉬움
    pattern_a = r"(쉬운|부담\s*없는|친숙한|노력이\s*적게|난이도가\s*낮은)"
    if re.search(pattern_a, ans_a):
        score += 1
        feedback.append("㉠ 정답 (1점): 쉬운 과제 특성 적절히 언급")
    else:
        feedback.append("㉠ 오답 (0점): '쉬운/친숙한/부담 없는' 등의 과제 특성이 누락됨")

    # ㉡ 검증: 혼자 + 집중/연습 (오개념 방지: 타인/함께 언급 시 오답)
    pattern_b_self = r"(혼자|독립|단독)"
    pattern_b_focus = r"(집중|연습|몰두|몰입)"
    wrong_b = r"(함께|다른\s*사람|모임|타인)"

    if re.search(wrong_b, ans_b):
        feedback.append("㉡ 오답 (0점 - 오개념): '타인과 함께함' 등 잘못된 환경 언급")
    elif re.search(pattern_b_self, ans_b) and re.search(pattern_b_focus, ans_b):
        score += 1
        feedback.append("㉡ 정답 (1점): '혼자'와 '집중/연습' 조건 모두 충족")
    else:
        feedback.append("㉡ 오답 (0점): '혼자' 및 '집중/연습' 관련 핵심 표현 부족")

    # ㉢ 검증: 학술 용어 (사회적 억제)
    ans_c_clean = ans_c.strip().replace(" ", "")
    if "사회적억제" in ans_c_clean:
        score += 1
        feedback.append("㉢ 정답 (1점): 정확한 학술 용어 기재")
    else:
        feedback.append("㉢ 오답 (0점): '사회적 억제' 용어 불일치")

    return score, feedback


def grade_set1_q2(method1, ans1, method2, ans2):
    """실전 적용-1 [서·논술형 2] 채점"""
    score = 0
    feedback = []

    # 중복 선택 차단
    if method1 == method2:
        return 0, ["오답 (전체 0점): (1)과 (2)에서 동일한 설명 방법을 중복 선택함"]

    methods = [(method1, ans1, "(1)번 문장"), (method2, ans2, "(2)번 문장")]
    
    # 설명 방법별 표지(Marker) 패턴
    markers = {
        "예시": r"(예를\s*들어|예컨대|사례로|~처럼)",
        "인과": r"(~기\s*때문에|~하여|그\s*결과|따라서|원인은)",
        "대조": r"(~와\s*달리|~인\s*반면|대조적으로|~지만)",
        "정의": r"(~란|~을\s*뜻한다|~을\s*의미한다|~라고\s*한다)"
    }

    # 지문 키워드 DB (1개 이상 필수)
    keywords = r"(쉬운\s*과제|어려운\s*과제|사회적\s*촉진|사회적\s*억제|혼자|함께|집중|모임|도서관)"

    for m_type, m_text, label in methods:
        m_score = 0
        # 1. 지문 키워드 포함 검증
        if not re.search(keywords, m_text):
            feedback.append(f"{label} 오답 (0점): 지문 핵심 키워드가 포함되지 않음")
            continue

        # 2. 선택한 설명 방법의 특성(표지) 구현 검증
        if re.search(markers[m_type], m_text):
            m_score += 2
            feedback.append(f"{label} 정답 (2점): [{m_type}]의 특성을 살려 지문 내용을 적절히 서술함")
        else:
            feedback.append(f"{label} 오답 (0점): 선택한 설명 방법[{m_type}]에 맞는 구문 표지(예: {markers[m_type]})가 문장에 드러나지 않음")
        
        score += m_score

    return score, feedback


def grade_set1_q3(visual_plan, visual_effect, audio_plan, audio_effect):
    """실전 적용-1 [서·논술형 3] 채점 (총 6점)"""
    score = 0
    feedback = []

    # [시각 연출 1점] 혼자/독립/책상 등 [장면 1]과 대비되는 연출
    vis_plan_pattern = r"(혼자|독립|책상|방|차분|단독)"
    if re.search(vis_plan_pattern, visual_plan):
        score += 1
        feedback.append("시각 연출 정답 (1점): [장면 1]과 대비되는 독립/혼자 있는 장면 연출")
    else:
        feedback.append("시각 연출 오답 (0점): '혼자/독립된 공간' 등 대비되는 연출 미비")

    # [시각 효과 2점] 지문 근거(어려운 과제/혼자 집중) + 효과
    vis_effect_kw = r"(어려운\s*과제|도전|집중|방해|사회적\s*억제)"
    if re.search(vis_effect_kw, visual_effect):
        score += 2
        feedback.append("시각 효과 정답 (2점): 지문 속 핵심 상황(어려운 과제/집중)을 근거로 효과 서술")
    else:
        feedback.append("시각 효과 오답 (0점): 지문 내용 근거 누락 (단순 일반론은 인정 불가)")

    # [청각 연출 1점] 정적/초침/배경음 없음
    aud_plan_pattern = r"(정적|고요|초침|배경음\s*없|소리\s*없)"
    if re.search(aud_plan_pattern, audio_plan):
        score += 1
        feedback.append("청각 연출 정답 (1점): [장면 1]과 대비되는 정적 연출")
    else:
        feedback.append("청각 연출 오답 (0점): 정적/고요함 등의 청각적 대비 요소 부족")

    # [청각 효과 2점] 지문 근거 + 효과
    aud_effect_kw = r"(소음|방해|혼자|집중|사회적\s*억제)"
    if re.search(aud_effect_kw, audio_effect):
        score += 2
        feedback.append("청각 효과 정답 (2점): 청각적 요인과 지문 내용(집중/억제) 간 연결 명확")
    else:
        feedback.append("청각 효과 오답 (0점): 지문 속 개념과의 연계성 미흡")

    return score, feedback

# ==========================================
# 2. Streamlit UI 화면 구성
# ==========================================

st.set_page_config(page_title="서·논술형 자동 채점 시스템", layout="wide")

st.title("📝 국어 서·논술형 문항 자동 채점 시스템")
st.caption("1~3번 세트 문항 채점 기준 및 정교한 규칙 알고리즘 기반 자동 채점 엔진")

st.sidebar.header("📌 세트 선택")
selected_set = st.sidebar.selectbox("채점할 문항 세트를 선택하세요", ["실전 적용-1 (사회적 촉진/억제)", "실전 적용-2 (정전기)", "실전 적용-3 (AI 그림)"])

if selected_set == "실전 적용-1 (사회적 촉진/억제)":
    st.header(" [실전 적용-1] 사회적 촉진과 사회적 억제 채점")
    
    tab1, tab2, tab3 = st.tabs(["서·논술형 1 (표 요약)", "서·논술형 2 (설명 방법)", "서·논술형 3 (영상 기획)"])
    
    with tab1:
        st.subheader("[서·논술형 1] 표 빈칸 채우기 (총 3점)")
        st.write("**지문 내용을 바탕으로 ㉠~㉢에 들어갈 적절한 말을 쓰시오.**")
        ans_a = st.text_input("㉠ 답안 입력:", placeholder="예: 비교적 쉬운 취미 생활이나 큰 노력이 들지 않는 과제")
        ans_b = st.text_input("㉡ 답안 입력:", placeholder="예: 차분하게 혼자 집중하는 시간을 가짐")
        ans_c = st.text_input("㉢ 답안 입력:", placeholder="예: 사회적 억제")
        
        if st.button("㉠~㉢ 채점하기"):
            score, feedback = grade_set1_q1(ans_a, ans_b, ans_c)
            st.metric("최종 점수", f"{score} / 3 점")
            for fb in feedback:
                st.write("- " + fb)

    with tab2:
        st.subheader("[서·논술형 2] 설명 방법을 활용한 문장 작성 (총 4점)")
        st.info("💡 **모범 답안 선택지 안내**: 예시, 인과, 대조, 정의 중 2개를 선택하여 문장을 완성하세요.")
        
        col1, col2 = st.compile_config if hasattr(st, 'compile_config') else (st.columns(2))
        with col1:
            m1 = st.selectbox("(1)번 설명 방법 선택:", ["대조", "예시", "인과", "정의"], key="m1")
            a1 = st.text_area("(1)번 문장 작성:", placeholder="예: 쉬운 과제는 함께할 때 효율이 높아지는 반면, 어려운 과제는 혼자 집중할 때 좋다.")
        
        with col2:
            m2 = st.selectbox("(2)번 설명 방법 선택:", ["예시", "대조", "인과", "정의"], key="m2")
            a2 = st.text_area("(2)번 문장 작성:", placeholder="예: 예를 들어, 복잡한 수학 문제나 공무원 시험 공부는 혼자서 연습하는 것이 좋다.")
            
        if st.button("설명문 채점하기"):
            score, feedback = grade_set1_q2(m1, a1, m2, a2)
            st.metric("최종 점수", f"{score} / 4 점")
            for fb in feedback:
                st.write("- " + fb)

    with tab3:
        st.subheader("[서·논술형 3] 영상 기획안 및 효과 서술 (총 6점)")
        v_plan = st.text_input("Ⓐ 시각 연출 계획 (1점):", placeholder="예: 조용한 방에서 학생 혼자 책상에 앉아 집중하는 모습을 보여준다.")
        v_eff = st.text_area("Ⓐ 시각 연출 효과 (2점):", placeholder="예: 혼자 공부하는 모습을 보여줌으로써, 어려운 과제는 혼자 차분히 집중해야 한다는 지문 내용을 강조한다.")
        
        a_plan = st.text_input("Ⓑ 청각 연출 계획 (1점):", placeholder="예: 배경음악 없이 시계 초침 소리만 잔잔하게 들리도록 한다.")
        a_eff = st.text_area("Ⓑ 청각 연출 효과 (2점):", placeholder="예: 주변 소음을 제거하여 방해받지 않고 혼자 집중해야 하는 '사회적 억제' 상황의 특성을 청각적으로 보여준다.")
        
        if st.button("영상 기획안 채점하기"):
            score, feedback = grade_set1_q3(v_plan, v_eff, a_plan, a_eff)
            st.metric("최종 점수", f"{score} / 6 점")
            for fb in feedback:
                st.write("- " + fb)

else:
    st.info("실전 적용-2 및 3 세트 채점 모듈도 동일한 규칙 기반으로 확장하여 탑재할 수 있습니다.")