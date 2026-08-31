"""Pydantic 数据模型 —— 入参校验与出参序列化"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_serializer

from core.times import to_iso_utc


class _UtcTimeMixin(BaseModel):
    """库中时间为 UTC（naive），序列化时统一补 +00:00 时区标识。

    前端 new Date() 依据时区标识自动换算本地时间；若无标识，
    无时区字符串会被当作本地时间解析，显示将比北京时间早 8 小时。
    """

    @field_serializer(
        "created_at", "started_at", "finished_at", "last_wrong_at",
        when_used="json", check_fields=False,
    )
    def _ser_utc(self, v):
        return to_iso_utc(v)


# ============ 认证 ============
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    nickname: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field("student", pattern="^(student|parent|admin)$")


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(_UtcTimeMixin):
    id: int
    username: str
    nickname: str
    role: str
    bind_code: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class BindChildRequest(BaseModel):
    bind_code: str


# ============ 科目 & 章节 ============
class SubjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    icon: str = "📚"
    grade: Optional[str] = None  # 年级/学段：文化课填"三年级"/"四年级"…；编程类无年级语义填占位"通用"。复合唯一约束 (name, grade) 的第二列。
    category: str = "culture"
    sort_order: int = 0
    question_count: int = 0
    available_types: List[str] = []  # 该科目实际包含的题型（去重），供前端动态显示/隐藏题型
    allowed_types: Optional[List[str]] = None  # 允许参与组卷/显示的题型（null/空=不限制）
    class Config:
        from_attributes = True


class TopicOut(BaseModel):
    id: int
    subject_id: int
    name: str
    unit: Optional[str] = None
    sort_order: int = 0
    question_count: int = 0  # 当前档位(tier 参数)下、排除弃用的有效题数
    valid_by_tier: dict = {}  # 各档位有效题数 {1: n, 2: n, 3: n}，供前端跨档显示/校验
    class Config:
        from_attributes = True


class SubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    icon: str = "📚"
    grade: Optional[str] = None  # 年级/学段：文化课填"三年级"/"四年级"…；编程类无年级语义填占位"通用"。详见 SubjectOut.grade。
    category: str = Field("culture", pattern="^(culture|programming)$")


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    grade: Optional[str] = None  # 年级/学段：文化课填"三年级"/"四年级"…；编程类无年级语义填占位"通用"。详见 SubjectOut.grade。修改不影响复合唯一 (name, grade)。
    category: Optional[str] = Field(None, pattern="^(culture|programming)$")
    allowed_types: Optional[List[str]] = None  # 允许参与组卷的题型；传空数组或 null 表示不限制


class TopicCreate(BaseModel):
    subject_id: int
    name: str
    unit: Optional[str] = None


class TopicUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    sort_order: Optional[int] = None


class UnitOut(BaseModel):
    """单元信息（文化类科目按单元分组用）"""
    unit: Optional[str] = None  # 单元名，None 表示"未分单元"
    topic_count: int = 0  # 该单元下的章节数
    question_count: int = 0  # 该单元下的题目总数


# ============ 题目 ============
class QuestionOut(BaseModel):
    id: int
    subject_id: int
    topic_id: int
    type: str
    content: str
    options: Optional[List[Any]] = None
    match_options: Optional[List[str]] = None  # 连线题右侧选项
    answer: Optional[str] = None  # 答题时不返回，提交后判分
    explanation: Optional[str] = None
    difficulty: int = 1
    tier: int = 1  # 分阶档位 1初级 2进阶 3挑战
    is_multiple: bool = False
    blank_count: int = 1
    blank_answers: Optional[List[str]] = None
    tolerance: float = 0.01
    topic_name: Optional[str] = None
    reading_items: Optional[List[Any]] = None  # 阅读理解子题数组
    deprecated: bool = False  # 弃用标记（不再出题，历史记录仍展示）
    class Config:
        from_attributes = True


class QuestionForExam(BaseModel):
    """答题时返回的题目（不含答案和讲解）"""
    id: int
    type: str
    content: str
    options: Optional[List[Any]] = None
    match_options: Optional[List[str]] = None  # 连线题右侧选项
    topic_name: Optional[str] = None
    difficulty: int = 1
    tier: int = 1  # 分阶档位 1初级 2进阶 3挑战
    explanation: Optional[str] = None  # code 题在答题时下发思路提示
    is_multiple: bool = False
    blank_count: int = 1
    reading_items: Optional[List[Any]] = None  # 阅读理解子题数组（不含子题 answer/explanation）


class QuestionCreate(BaseModel):
    subject_id: int
    topic_id: int
    type: str = Field(..., pattern="^(choice|judge|fill|essay|code|match|sort|reading)$")
    content: str
    options: Optional[List[Any]] = None
    match_options: Optional[List[str]] = None  # 连线题右侧选项
    reading_items: Optional[List[Any]] = None  # 阅读理解子题数组
    answer: str
    explanation: Optional[str] = None
    difficulty: int = 1
    tier: int = 1  # 分阶档位 1初级 2进阶 3挑战
    is_multiple: bool = False
    blank_count: int = 1
    blank_answers: Optional[List[str]] = None
    tolerance: float = 0.01
    expected_output: Optional[str] = None  # 编程题：参考代码运行后的预期输出
    sample_input: Optional[str] = None  # 编程题：参考代码 input() 需要的 stdin 样例


class QuestionUpdate(BaseModel):
    topic_id: Optional[int] = None
    type: Optional[str] = Field(None, pattern="^(choice|judge|fill|essay|code|match|sort|reading)$")
    content: Optional[str] = None
    options: Optional[List[Any]] = None
    match_options: Optional[List[str]] = None  # 连线题右侧选项
    reading_items: Optional[List[Any]] = None  # 阅读理解子题数组
    answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[int] = None
    tier: Optional[int] = None  # 分阶档位（更新时可改）
    is_multiple: Optional[bool] = None
    blank_count: Optional[int] = None
    blank_answers: Optional[List[str]] = None
    tolerance: Optional[float] = None
    expected_output: Optional[str] = None  # 编程题：参考代码运行后的预期输出
    sample_input: Optional[str] = None  # 编程题：参考代码 input() 需要的 stdin 样例


# ============ 答题 ============
class ExamStartRequest(BaseModel):
    """组卷请求"""
    subject_id: int
    topic_ids: List[int] = Field(default=[], description="章节ID，空表示全部")
    types: List[str] = Field(default=[], description="题型，空表示全部")
    count: int = Field(10, ge=1, le=100)
    mode: str = Field("custom", pattern="^(custom|wrong|random)$")
    tier: int = Field(1, description="分阶档位 1初级 2进阶 3挑战，默认初级")


class AvailableCountOut(BaseModel):
    """组卷可用题数（与 start_exam 抽题池逻辑完全一致，不含 count 截断）。
    前端可用它在选择课时/tier 变化时判断：合计可用题数 < 50 时禁用「50题」选项。"""
    available: int


class AnswerItem(BaseModel):
    question_id: int
    user_answer: Optional[str] = None


class ExamSubmitRequest(BaseModel):
    subject_id: int
    mode: str = "custom"
    topic_ids: List[int] = []
    answers: List[AnswerItem]
    duration_seconds: int = 0
    tier: int = Field(1, description="分阶档位 1初级 2进阶 3挑战，与 start 一致")


class AnswerRecordOut(BaseModel):
    id: int
    question_id: int
    user_answer: Optional[str] = None
    run_output: Optional[str] = None  # 编程题：后台实跑后的输出 / 判分说明
    is_correct: Optional[bool] = None  # 对错标记（老数据可能为 NULL，前端需兼容）
    llm_score: Optional[int] = None   # 统一评分 0-100（所有题型）
    llm_stars: Optional[int] = None   # 星级 0-5
    llm_feedback: Optional[str] = None  # LLM 鼓励性反馈（仅编程题有）
    question: Optional[QuestionOut] = None
    class Config:
        from_attributes = True


class MasteryRewardOut(BaseModel):
    """精通奖励发放明细（交卷后弹窗展示）"""
    subject_name: str
    topic_name: str
    tier: int
    points: int
    mode: str  # new=新达成 / retroactive=历史补发


class MasteryDeltaOut(BaseModel):
    """精通度变化（答题前后对比）"""
    topic_name: str             # 课程名
    before_pct: int             # 答题前精通度百分比（0-100）
    after_pct: int              # 答题后精通度百分比（0-100）
    delta: int                  # 变化量（after - before，可正可0不可负）
    newly_mastered: bool        # 本次是否新达到精通
    bottleneck: Optional[str] = None  # 未提升时的瓶颈原因 key（rate/coverage/count）


class ExamRecordOut(_UtcTimeMixin):
    id: int
    subject_id: int
    subject_name: Optional[str] = None
    mode: str
    total: int
    correct: int
    wrong: int
    score: int
    duration_seconds: int
    started_at: datetime
    finished_at: Optional[datetime] = None
    tier: int = 1  # 本次答题所选分阶档位
    answer_records: List[AnswerRecordOut] = []
    points_earned: int = 0  # 本次答题按 scoring_rules 获得的积分
    mastery_rewards: List[MasteryRewardOut] = []  # 本次触发的精通奖励（含历史补发）
    mastery_deltas: List[MasteryDeltaOut] = []    # 本次答题的精通度变化（逐课）
    class Config:
        from_attributes = True


class ExamStartResponse(BaseModel):
    questions: List[QuestionForExam]
    requested_count: int = 0   # 学员请求的题数档位
    actual_count: int = 0      # 实际发题数（题池不足时自动降档）
    downgraded: bool = False   # 是否因题池不足被降档


# ============ 错题本 ============
class WrongQuestionOut(_UtcTimeMixin):
    id: int
    question_id: int
    wrong_count: int
    last_wrong_at: datetime
    mastered: bool
    question: Optional[QuestionOut] = None
    # 错题最近一次作答快照（用于 code 题复盘，默认 None 兼容老数据）
    user_answer: Optional[str] = None
    run_output: Optional[str] = None
    llm_feedback: Optional[str] = None
    subject_name: Optional[str] = None
    class Config:
        from_attributes = True


# ============ 统计 ============
class SubjectStats(BaseModel):
    subject_id: int
    subject_name: str
    exam_count: int
    avg_score: float
    best_score: int
    wrong_count: int
    question_count: int


class StatsOverview(BaseModel):
    total_exams: int
    avg_score: float
    best_score: int
    total_wrong: int
    subjects: List[SubjectStats] = []
