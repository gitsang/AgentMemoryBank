export type TabId = 'points' | 'fines' | 'speeds' | 'times' | 'signs' | 'gestures' | 'docs';

export type PointRow = {
  action: string;
  note: string;
};

export type FineRow = {
  amount: string;
  range: string;
  note: string;
};

export type SpeedRow = {
  scenario: string;
  limit: string;
  note: string;
};

export type TimeRow = {
  item: string;
  value: string;
  note: string;
};

export type SignRow = {
  type: string;
  shape: string;
  color: string;
  desc: string;
};

export type GestureRow = {
  name: string;
  desc: string;
};

export type DocumentRow = {
  item: string;
  detail: string;
};

// Final-review facts are intentionally kept in this data module so legal/exam
// updates can be reviewed in one place instead of buried inside JSX markup.
export const TABS: {id: TabId; label: string}[] = [
  {id: 'points', label: '记分'},
  {id: 'fines', label: '罚款'},
  {id: 'speeds', label: '速度'},
  {id: 'times', label: '时间'},
  {id: 'signs', label: '标志标线'},
  {id: 'gestures', label: '交警手势'},
  {id: 'docs', label: '证件相关'},
];

export const POINTS_12: PointRow[] = [
  {action: '酒驾（饮酒后驾驶机动车）', note: ''},
  {action: '逃逸（造成事故后逃逸，尚不构成犯罪）', note: ''},
  {action: '伪造、变造或使用伪造、变造的机动车牌证', note: ''},
  {action: '高速公路倒车、逆行、穿越中央分隔带掉头', note: '高速场景'},
  {action: '高速/城市快速路超速50%以上（普通机动车）', note: '严重超速'},
  {action: '代替他人接受处罚和记分牟利', note: '卖分'},
];

export const POINTS_9: PointRow[] = [
  {action: '高速违法停车', note: ''},
  {action: '未悬挂号牌或故意遮挡、污损号牌', note: '常见陷阱'},
  {action: '与准驾车型不符', note: ''},
  {action: '连续驾驶中型以上客车/危运车超4小时未休息或休息少于20分钟', note: '疲劳驾驶'},
];

export const POINTS_6: PointRow[] = [
  {action: '违反道路交通信号灯通行（闯红灯）', note: ''},
  {action: '占用应急车道行驶', note: '高速/城市快速路'},
  {action: '不按规定避让校车', note: ''},
  {action: '低能见度气象条件下高速不按规定行驶', note: ''},
  {action: '驾驶证被暂扣/扣留期间仍驾驶机动车', note: ''},
];

export const POINTS_3: PointRow[] = [
  {action: '货车超载30%~50%或违规载客', note: ''},
  {action: '行驶超速20%~50%', note: '高速/快速路以外'},
  {action: '不按规定超车、让行', note: ''},
  {action: '拨打、接听手持电话等妨碍安全驾驶', note: ''},
  {action: '不按规定安装机动车号牌', note: ''},
  {action: '行经人行横道不减速、不停车、不避让行人', note: ''},
];

export const POINTS_1: PointRow[] = [
  {action: '不按规定使用灯光', note: ''},
  {action: '违反禁令标志、禁止标线', note: ''},
  {action: '货车超载未达30%', note: ''},
  {action: '高速/快速路以外不按规定倒车、掉头', note: ''},
];

export const FINES: FineRow[] = [
  {amount: '20-200元', range: '警告或20-200元', note: '轻微违法行为'},
  {amount: '200-2000元', range: '200-2000元罚款', note: '一般违法行为'},
  {amount: '200-2000元+可拘留', range: '罚款+15日以下拘留', note: '无证驾驶、事故逃逸等'},
  {amount: '200-2000元+可吊销', range: '罚款+吊销驾驶证', note: '超速50%以上、驾驶拼装/报废车'},
  {amount: '500-2000元', range: '500-2000元', note: '货运机动车超载30%以上或违规载客'},
  {amount: '1000-2000元', range: '1000-2000元+暂扣6个月', note: '饮酒后首次酒驾'},
  {amount: '2000-5000元', range: '2000-5000元+可拘留', note: '伪造、变造或使用伪造变造牌证'},
];

export const SPEEDS: SpeedRow[] = [
  {scenario: '无道路中心线城市道路', limit: '30 km/h', note: ''},
  {scenario: '同方向只有1条机动车道的城市道路', limit: '50 km/h', note: ''},
  {scenario: '无道路中心线公路', limit: '40 km/h', note: ''},
  {scenario: '同方向只有1条机动车道的公路', limit: '70 km/h', note: ''},
  {scenario: '高速公路最低限速', limit: '60 km/h', note: ''},
  {scenario: '高速公路最高限速', limit: '120 km/h', note: ''},
  {scenario: '同方向2车道高速左车道最低', limit: '100 km/h', note: ''},
  {scenario: '能见度<200m（高速）限速 60', limit: '60 km/h', note: ''},
  {scenario: '能见度<100m（高速）限速 40', limit: '40 km/h', note: ''},
  {scenario: '能见度<50m（高速）限速 20', limit: '20 km/h', note: ''},
  {scenario: '掉头/转弯/狭窄路段/窄桥/急弯', limit: '30 km/h', note: ''},
  {scenario: '冰雪泥泞路', limit: '30 km/h', note: ''},
  {scenario: '进出非机动车道/雾/沙尘/冰雹', limit: '30 km/h', note: ''},
];

export const TIMES: TimeRow[] = [
  {item: '考试时长', value: '45 分钟', note: '科目一'},
  {item: '题量', value: '100 题', note: ''},
  {item: '合格标准', value: '90分及以上', note: ''},
  {item: '驾驶证有效期（初次）', value: '6 年', note: ''},
  {item: '换证提前期限', value: '90 日', note: '有效期满前'},
  {item: '实习期', value: '12 个月', note: ''},
  {item: '70周岁以上驾驶人', value: '每年', note: '提交身体条件证明'},
  {item: '满分教育考试（记满12分）', value: '7天学习', note: ''},
  {item: '信息变更备案', value: '30 日', note: ''},
  {item: '交通事故报警时限', value: '立即', note: ''},
];

export const SIGNS: SignRow[] = [
  {type: '警告标志', shape: '等边三角形', color: '黄底黑边', desc: '注意危险、注意行人、急弯等'},
  {type: '禁令标志', shape: '圆形', color: '白底红圈红斜杠', desc: '禁止通行、禁止停车、限速等'},
  {type: '指示标志', shape: '圆形或方形', color: '蓝底白图案', desc: '直行、转弯、停车位等'},
  {type: '指路标志', shape: '矩形', color: '蓝底/绿底白字', desc: '地名、方向、距离等'},
  {type: '旅游区标志', shape: '矩形', color: '棕底白字', desc: '旅游景点方向和距离'},
  {type: '施工标志', shape: '矩形', color: '橙底黑字', desc: '道路施工信息'},
  {type: '辅助标志', shape: '矩形', color: '白底黑字', desc: '附在主标志下方，补充说明时、车种等'},
];

export const GESTURES: GestureRow[] = [
  {name: '停止信号', desc: '左臂向前上方直伸，掌心向前'},
  {name: '直行信号', desc: '左臂向左平伸，右臂向右平伸后向左摆动'},
  {name: '左转弯信号', desc: '右臂向前平伸，左臂向右前方摆动'},
  {name: '左转弯待转信号', desc: '左臂向左下方平伸，掌心向下并向下摆动'},
  {name: '右转弯信号', desc: '左臂向前平伸，右臂向左前方摆动'},
  {name: '变道信号', desc: '右臂向前平伸，掌心向左，向左水平摆动'},
  {name: '减速慢行信号', desc: '右臂向前平伸，掌心向下，上下摆动'},
  {name: '示意车辆靠边停车', desc: '左臂向前上方伸，右臂向左水平摆动'},
];

export const DOCUMENTS: DocumentRow[] = [
  {item: '准驾车型对比', detail: '本页以 C1 为主；A/B/D/E/F/M/N/P 仅用于识别准驾车型分类题中的干扰项'},
  {item: 'C1准驾车型', detail: '小型、微型载客汽车，轻型、微型载货汽车，轻型、微型专项作业车'},
  {item: 'C2准驾车型', detail: '小型微型自动挡载客汽车、轻型微型自动挡载货汽车'},
  {item: '驾驶证补证', detail: '向驾驶证核发地或者核发地以外的车辆管理所申请'},
  {item: '驾驶证换证', detail: '有效期满前90日内'},
  {item: '不得申请驾驶证情形', detail: '红绿色盲、癫痫、精神病、痴呆等妨碍安全驾驶的疾病'},
  {item: '注销驾驶证情形', detail: '死亡、身体条件不适合、申请注销、丧失民事行为能力等'},
  {item: '吊销驾驶证情形', detail: '酒醉驾/超速50%/逃逸/驾驶报废车等重大违法'},
];
