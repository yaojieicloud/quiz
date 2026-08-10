"""ORM 模型 —— 支持多科目、多用户、答题记录与错题追踪"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint, Float
)
from sqlalchemy.orm import relationship

from database import Base
from database import Base, engine


class User(Base):
    """用户表：学生 / 家长 / 管理员"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    nickname = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="student", nullable=False)  # student / parent / admin
    bind_code = Column(String(20), unique=True, index=True)  # 学生生成，家长输入后绑定
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    exam_records = relationship("ExamRecord", back_populates="user", cascade="all, delete-orphan")
    wrong_questions = relationship("WrongQuestion", back_populates="user", cascade="all, delete-orphan")
    parent_links = relationship("ParentChild", back_populates="parent", foreign_keys="ParentChild.parent_id")
    child_links = relationship("ParentChild", back_populates="child", foreign_keys="ParentChild.child_id")


class ParentChild(Base):
    """家长-孩子绑定关系"""
    __tablename__ = "parent_child"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    child_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("parent_id", "child_id", name="uq_parent_child"),)

    parent = relationship("User", back_populates="parent_links", foreign_keys=[parent_id])
    child = relationship("User", back_populates="child_links", foreign_keys=[child_id])


class Subject(Base):
    """科目表：Python / 数学 / 语文 ...

    category:
      - culture: 文化类（语文/数学/英语...），按"单元+课时"两级组织
      - programming: 编程类（Python...），按"课"扁平组织
    """
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    icon = Column(String(20), default="📚")  # emoji 图标
    grade = Column(String(20))  # 学段，如"三年级"、"入门"
    category = Column(String(20), default="culture", nullable=False)  # culture / programming
    sort_order = Column(Integer, default=0)
    # 该科目允许参与组卷/显示的题型列表（JSON 数组）。
    # NULL 或空 = 不限制（该科目实际有的题型都参与）。
    # 例如语文/英语可配置关闭 essay，数学保留 essay。
    allowed_types = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="subject", cascade="all, delete-orphan")


class Topic(Base):
    """章节/知识点表

    unit: 所属单元（仅文化类科目使用，编程类留空）。
    文化类前端按 unit 分组折叠展示；编程类扁平多选。
    """
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    unit = Column(String(100), nullable=True)  # 单元名，文化类填，编程类留空
    sort_order = Column(Integer, default=0)

    subject = relationship("Subject", back_populates="topics")
    questions = relationship("Question", back_populates="topic")


class Question(Base):
    """题目表 —— 兼容选择/判断/填空/问答/编程/连线/排序七种题型

    type:
      - choice: 选择题（单选/多选），options 为选项数组，answer 为正确索引
                多选题用 is_multiple=True 标记，answer 存逗号分隔索引如 "0,2"
      - judge:  判断题，options 为 ["对","错"]，answer 为 0(对) 或 1(错)
      - fill:   填空题，单空 answer 存标准答案；多空 blank_answers 存 JSON 数组
                blank_count 记录空的数量，tolerance 支持数字容差
      - essay:  应用题，无标准答案，LLM 评星反馈（降级：有内容即通过）
      - code:   编程题，沙箱实跑 + LLM 评星
      - match:  连线题，options 为左侧项目，answer 存 "左索引:右索引,左索引:右索引"
      - sort:   排序题，options 为打乱的项目，answer 存正确顺序索引如 "1,0,2,3"
      - reading: 阅读理解题，content 为文章正文，reading_items 存子题数组（JSON）
                 answer 存子题答案索引串如 "1,0,2"，判分按子题比例给分
    """
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False, index=True)
    type = Column(String(20), nullable=False)  # choice / judge / fill / essay / code / match / sort / reading
    content = Column(Text, nullable=False)  # 题干（可含 HTML）；reading 题为文章正文
    options = Column(JSON)  # 选择/判断题的选项数组；fill/essay/code/reading 为 null
    match_options = Column(JSON)  # 连线题右侧选项数组（仅 match 类型用）
    reading_items = Column(JSON)  # 阅读理解子题数组（仅 reading 类型用）
    # 子题格式: [{"type":"choice","q":"问题","options":[...],"answer":"1","explanation":"讲解"}, ...]
    # 当前版本子题仅支持 choice；type 字段预留 judge/fill/essay 扩展
    answer = Column(String(500), nullable=False)  # 索引或字符串答案；reading 为子题答案索引串
    explanation = Column(Text)  # 讲解（可含 HTML）
    difficulty = Column(Integer, default=1)  # 1简单 2中等 3较难
    # 多选题标记（仅 choice 类型用）
    is_multiple = Column(Boolean, default=False)
    # 填空题多空支持（仅 fill 类型用）
    blank_count = Column(Integer, default=1)
    blank_answers = Column(JSON)  # ["答案1", "答案2", ...]
    tolerance = Column(Float, default=0.01)  # 数字容差（fill 题用）
    # 编程题判分用：参考代码运行的预期输出 + 需要的 stdin 样例
    expected_output = Column(Text)  # 参考代码运行后的预期 stdout（判分比对）
    sample_input = Column(Text, default="")  # 参考代码里 input() 需要的 stdin 样例
    # 弃用标记：被标记为弃用的题目不再进入任何出题（组卷/错题重做），
    # 但仍保留在库中以正确展示历史答题记录。用于清理重复选项等质量问题的旧题。
    deprecated = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    subject = relationship("Subject", back_populates="questions")
    topic = relationship("Topic", back_populates="questions")
    answer_records = relationship("AnswerRecord", back_populates="question")
    wrong_records = relationship("WrongQuestion", back_populates="question")


class ExamRecord(Base):
    """考试记录：一次完整答题"""
    __tablename__ = "exam_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    subject_name = Column(String(50))  # 冗余存储，便于历史记录展示
    mode = Column(String(20), default="custom")  # custom / wrong / random
    total = Column(Integer, nullable=False)
    correct = Column(Integer, default=0)
    wrong = Column(Integer, default=0)
    score = Column(Integer, default=0)  # 0-100
    duration_seconds = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)

    user = relationship("User", back_populates="exam_records")
    answer_records = relationship("AnswerRecord", back_populates="exam_record", cascade="all, delete-orphan")


class AnswerRecord(Base):
    """单题作答明细"""
    __tablename__ = "answer_records"

    id = Column(Integer, primary_key=True, index=True)
    exam_record_id = Column(Integer, ForeignKey("exam_records.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_answer = Column(String(500))  # 用户提交的答案
    run_output = Column(Text)  # 编程题：后台实跑孩子代码后的 stdout / 判分说明
    is_correct = Column(Boolean, default=False)
    # LLM 评分（仅编程题使用，NULL 表示未调用 LLM）
    llm_score = Column(Integer, nullable=True)   # LLM 给的分数 0-100
    llm_stars = Column(Integer, nullable=True)   # LLM 给的星级 0-5
    llm_feedback = Column(Text, nullable=True)   # LLM 给的鼓励性反馈
    time_used = Column(Integer, default=0)  # 该题用时(秒)

    exam_record = relationship("ExamRecord", back_populates="answer_records")
    question = relationship("Question", back_populates="answer_records")


class WrongQuestion(Base):
    """错题本：去重累积，记录错误次数"""
    __tablename__ = "wrong_questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    wrong_count = Column(Integer, default=1)
    last_wrong_at = Column(DateTime, default=datetime.utcnow)
    mastered = Column(Boolean, default=False)  # 是否已掌握（错题重做答对后标记）

    user = relationship("User", back_populates="wrong_questions")
    question = relationship("Question", back_populates="wrong_records")
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_user_question"),)


class AIReport(Base):
    """AI 周报：存储 LLM 生成的学习报告"""
    __tablename__ = "ai_reports"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    student_name = Column(String(50), nullable=False)  # 冗余存储，避免学员改名影响历史
    report_text = Column(Text, nullable=False)  # LLM 生成的周报正文
    data_summary = Column(JSON, nullable=False)  # 生成时的数据快照（图表渲染用）
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# 积分系统 + 大转盘抽奖（阶段 1）
# 设计原则：参数全可配置、概率服务端决定、原子记账、预留盲盒(mode)扩展。
# 详见 docs/积分系统与大转盘方案.md
# ============================================================================

class ScoringRule(Base):
    """积分换算矩阵（题数 × 得分段 → 积分），可配置"""
    __tablename__ = "scoring_rules"

    id = Column(Integer, primary_key=True, index=True)
    question_count = Column(Integer, nullable=False, index=True)  # 题数：10/20/50
    score_band = Column(Integer, nullable=False, index=True)      # 得分段：80/90/100
    points = Column(Integer, nullable=False)                     # 对应积分
    is_active = Column(Boolean, default=True, nullable=False)    # 是否启用


class StudentPoints(Base):
    """学员积分余额缓存（独立表，不改动 users 表）"""
    __tablename__ = "student_points"

    student_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    balance = Column(Integer, default=0, nullable=False)         # 当前积分
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PointsLedger(Base):
    """积分流水（审计用）"""
    __tablename__ = "points_ledger"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    delta = Column(Integer, nullable=False)        # 正=获得，负=消耗
    reason = Column(String(20), nullable=False)    # exam_reward / wheel_spin / direct_redeem / adjust
    ref_id = Column(Integer, nullable=True)        # 关联 exam_records.id / plays.id / direct_redemptions.id
    balance_after = Column(Integer, nullable=False)  # 变动后余额（冗余）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class WheelPrize(Base):
    """转盘/盲盒奖品池（可配置，mode 区分玩法以支持扩展）"""
    __tablename__ = "wheel_prizes"

    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String(20), default="wheel", nullable=False, index=True)  # wheel / blindbox（预留）
    name = Column(String(100), nullable=False)      # 奖品名
    type = Column(String(20), default="physical", nullable=False)  # virtual / physical
    virtual_payload = Column(String(100), nullable=True)  # 虚拟载荷（如 "+2积分"），physical 时为 null
    weight = Column(Integer, default=1, nullable=False)   # 概率权重
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0)


class Play(Base):
    """通用抽奖/开箱记录（覆盖大转盘与未来盲盒）"""
    __tablename__ = "plays"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mode = Column(String(20), default="wheel", nullable=False, index=True)  # wheel / blindbox
    prize_id = Column(Integer, ForeignKey("wheel_prizes.id"), nullable=False)
    prize_name = Column(String(100), nullable=False)   # 冗余快照
    is_physical = Column(Boolean, default=True, nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # pending / redeemed / granted
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    redeemed_at = Column(DateTime, nullable=True)
    redeemed_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class DirectRedemption(Base):
    """直兑商城兑换记录"""
    __tablename__ = "direct_redemptions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    item_id = Column(Integer, ForeignKey("redeem_items.id"), nullable=False)
    cost = Column(Integer, nullable=False)   # 扣减积分快照
    status = Column(String(20), default="pending", nullable=False)  # pending / redeemed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    redeemed_at = Column(DateTime, nullable=True)
    redeemed_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class RedeemItem(Base):
    """直兑商城配置（可配置）"""
    __tablename__ = "redeem_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), default="physical", nullable=False)  # virtual / physical
    cost = Column(Integer, nullable=False)          # 积分价格
    virtual_payload = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0)


class Config(Base):
    """全局键值配置（抽奖费、弹窗版本号等，均可配置）"""
    __tablename__ = "config"

    key = Column(String(50), primary_key=True)
    value = Column(String(200), nullable=False)


# ============================================================================
# LLM 调用记录（兜底 + 追溯审计）
# 每次 LLM 调用（评分 / 周报等）无论成败都落一条；先试 aliyun，失败再 deepseek，
# 各自记一条，便于事后分析「走了哪个模型、消耗多少 token、耗时、成败原因」。
# ============================================================================

class LLMCall(Base):
    """LLM 调用审计日志（可追溯每次调用的 provider / 模型 / token 消耗 / 耗时 / 成败）"""
    __tablename__ = "llm_calls"

    id = Column(Integer, primary_key=True, index=True)
    scenario = Column(String(40), nullable=False, index=True)     # 调用场景：code_grade / weekly_report / ...
    provider = Column(String(20), nullable=False, index=True)      # aliyun / deepseek
    model = Column(String(40), nullable=False)                    # 实际使用的模型名
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    status = Column(String(10), nullable=False)                   # success / failed
    latency_ms = Column(Integer, nullable=True)                   # 本次调用耗时（毫秒）
    error = Column(Text, nullable=True)                           # 失败原因（截断存储）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
