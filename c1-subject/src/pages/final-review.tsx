import {useState} from 'react';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import {
  DOCUMENTS,
  FINES,
  GESTURES,
  POINTS_1,
  POINTS_12,
  POINTS_3,
  POINTS_6,
  POINTS_9,
  SIGNS,
  SPEEDS,
  TABS,
  TIMES,
  type TabId,
} from '../data/final-review';
import styles from './final-review.module.css';

const cellColor = (pts: number): string => {
  if (pts >= 12) return styles.cell12;
  if (pts >= 9) return styles.cell9;
  if (pts >= 6) return styles.cell6;
  if (pts >= 3) return styles.cell3;
  return styles.cell1;
};

function Section({title, children}: {title: string; children: React.ReactNode}) {
  return (
    <div className={styles.section}>
      <Heading as="h3" className={styles.sectionTitle}>{title}</Heading>
      {children}
    </div>
  );
}

function TableFrame({children}: {children: React.ReactNode}) {
  return <div className={styles.tableFrame}>{children}</div>;
}

function PointsTab() {
  return (
    <>
      <div className={styles.tipBlock}>
        <strong>口诀</strong>：12分看行为严重性（酒驾、逃逸、伪造、高速逆行），6分看信号灯与应急车道
      </div>

      <Section title="一次记12分">
        <TableFrame>
          <table className={styles.densityTable}>
            <thead><tr><th>违法行为</th><th>备注</th></tr></thead>
            <tbody>
              {POINTS_12.map((r, i) => (
                <tr key={i} className={r.note ? styles.trapRow : undefined}>
                  <td>{r.action}</td>
                  <td>{r.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableFrame>
      </Section>

      <Section title="一次记9分">
        <TableFrame>
          <table className={styles.densityTable}>
            <thead><tr><th>违法行为</th><th>备注</th></tr></thead>
            <tbody>
              {POINTS_9.map((r, i) => (
                <tr key={i} className={r.note ? styles.trapRow : undefined}>
                  <td>{r.action}</td>
                  <td>{r.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableFrame>
      </Section>

      <Section title="一次记6分">
        <TableFrame>
          <table className={styles.densityTable}>
            <thead><tr><th>违法行为</th><th>备注</th></tr></thead>
            <tbody>
              {POINTS_6.map((r, i) => (
                <tr key={i} className={r.note ? styles.trapRow : undefined}>
                  <td>{r.action}</td>
                  <td>{r.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableFrame>
      </Section>

      <Section title="一次记3分">
        <TableFrame>
          <table className={styles.densityTable}>
            <thead><tr><th>违法行为</th><th>备注</th></tr></thead>
            <tbody>
              {POINTS_3.map((r, i) => (
                <tr key={i} className={r.note ? styles.trapRow : undefined}>
                  <td>{r.action}</td>
                  <td>{r.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableFrame>
      </Section>

      <Section title="一次记1分">
        <TableFrame>
          <table className={styles.densityTable}>
            <thead><tr><th>违法行为</th><th>备注</th></tr></thead>
            <tbody>
              {POINTS_1.map((r, i) => (
                <tr key={i} className={r.note ? styles.trapRow : undefined}>
                  <td>{r.action}</td>
                  <td>{r.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableFrame>
      </Section>
    </>
  );
}

function FinesTab() {
  return (
    <>
      <div className={styles.mnemonic}>罚款速记：小20~200，中200~2000，大500~2000，酒驾1000~2000</div>
      <TableFrame>
        <table className={styles.densityTable}>
          <thead><tr><th>罚款幅度</th><th>描述</th><th>典型行为</th></tr></thead>
          <tbody>
            {FINES.map((r, i) => (
              <tr key={i}>
                <td><strong>{r.amount}</strong></td>
                <td>{r.range}</td>
                <td>{r.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableFrame>
    </>
  );
}

function SpeedsTab() {
  return (
    <>
      <div className={styles.mnemonic}>
        无线城三公四 · 一线城五公七 · 高速60~120
      </div>

      <Section title="道路限速（无特殊标志时）">
        <TableFrame>
          <table className={styles.densityTable}>
            <thead><tr><th>场景</th><th>限速</th><th>备注</th></tr></thead>
            <tbody>
              {SPEEDS.filter((_, i) => i < 4).map((r, i) => (
                <tr key={i}>
                  <td>{r.scenario}</td>
                  <td className={cellColor(12)}><strong>{r.limit}</strong></td>
                  <td>{r.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableFrame>
      </Section>

      <Section title="高速公路限速">
        <TableFrame>
          <table className={styles.densityTable}>
            <thead><tr><th>场景</th><th>限速</th><th>备注</th></tr></thead>
            <tbody>
              {SPEEDS.filter((_, i) => i >= 4 && i < 7).map((r, i) => (
                <tr key={i}>
                  <td>{r.scenario}</td>
                  <td className={cellColor(3)}><strong>{r.limit}</strong></td>
                  <td>{r.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableFrame>
      </Section>

      <Section title="特殊天气/场景限速">
        <TableFrame>
          <table className={styles.densityTable}>
            <thead><tr><th>场景</th><th>限速</th><th>备注</th></tr></thead>
            <tbody>
              {SPEEDS.filter((_, i) => i >= 7).map((r, i) => (
                <tr key={i}>
                  <td>{r.scenario}</td>
                  <td><strong>{r.limit}</strong></td>
                  <td>{r.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </TableFrame>
      </Section>

      <div className={styles.tipBlock}>
        <strong>能见度口诀</strong>：261、145、520（能见度200m-限速60-距离100m；100m-限速40-距离50m；50m-限速20-尽快驶离高速）
      </div>
    </>
  );
}

function TimesTab() {
  return (
    <>
      <TableFrame>
        <table className={styles.densityTable}>
          <thead><tr><th>项目</th><th>数值</th><th>备注</th></tr></thead>
          <tbody>
            {TIMES.map((r, i) => (
              <tr key={i}>
                <td>{r.item}</td>
                <td><strong>{r.value}</strong></td>
                <td>{r.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableFrame>
    </>
  );
}

function SignsTab() {
  return (
    <>
      <div className={styles.mnemonic}>三角黄警告，圆红白禁令，蓝圆指示，蓝绿指路，棕底旅游区</div>
      <TableFrame>
        <table className={styles.densityTable}>
          <thead><tr><th>类型</th><th>形状</th><th>颜色</th><th>常见内容</th></tr></thead>
          <tbody>
            {SIGNS.map((r, i) => (
              <tr key={i}>
                <td><strong>{r.type}</strong></td>
                <td>{r.shape}</td>
                <td>{r.color}</td>
                <td>{r.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </TableFrame>

      <Section title="易混淆标志辨析">
        <div className={styles.quickCard}>
          <h4>禁停 vs 禁长停 vs 允许停车</h4>
          <ul>
            <li>🚫 红圈蓝底 + 红叉 = 禁止停车（临时也不行）</li>
            <li>🚫 红圈蓝底 + 单斜杠 = 禁止长时间停车（可临时）</li>
            <li>蓝底 P = 允许停车</li>
          </ul>
        </div>
        <div className={styles.quickCard}>
          <h4>警告标志形状统一为等边三角形</h4>
          <ul>
            <li>方向指示标志为箭头形</li>
            <li>注意标志均为黄底黑图案</li>
          </ul>
        </div>
      </Section>
    </>
  );
}

function GesturesTab() {
  return (
    <>
      <div className={styles.mnemonic}>先看交警方位，再看手臂位置与摆动方向</div>
      <div className={styles.gestureGrid}>
        {GESTURES.map((g, i) => (
          <div className={styles.gestureCard} key={i}>
            <div className={styles.gestureName}>{g.name}</div>
            <div className={styles.gestureDesc}>{g.desc}</div>
          </div>
        ))}
      </div>

      <Section title="手势判别要点">
        <div className={styles.quickCard}>
          <h4>停止信号</h4>
          <ul><li>左臂前上伸，掌心向前 — 面向你=停车，不面向你也可能停车</li></ul>
        </div>
        <div className={styles.quickCard}>
          <h4>左转 vs 右转</h4>
          <ul>
            <li>左转：右臂前伸，左臂向右前方摆动</li>
            <li>右转：左臂前伸，右臂向左前方摆动</li>
          </ul>
        </div>
        <div className={styles.quickCard}>
          <h4>变道 vs 减速</h4>
          <ul>
            <li>右臂平伸 + 水平摆动 = 变道</li>
            <li>右臂平伸 + 上下摆动 = 减速</li>
          </ul>
        </div>
      </Section>
    </>
  );
}

function DocsTab() {
  return (
    <>
      {DOCUMENTS.map((d, i) => (
        <div className={styles.quickCard} key={i}>
          <h4>{d.item}</h4>
          <p style={{margin: 0, fontSize: '0.85rem'}}>{d.detail}</p>
        </div>
      ))}
    </>
  );
}

const TAB_COMPONENTS: Record<TabId, React.FC> = {
  points: PointsTab,
  fines: FinesTab,
  speeds: SpeedsTab,
  times: TimesTab,
  signs: SignsTab,
  gestures: GesturesTab,
  docs: DocsTab,
};

export default function FinalReviewPage() {
  const [activeTab, setActiveTab] = useState<TabId>('points');
  const ActiveComponent = TAB_COMPONENTS[activeTab];

  return (
    <Layout title="考前速查" description="C1 科目一考前高密度速查手册">
      <main className={styles.page}>
        <div className={styles.header}>
          <Heading as="h1">科目一考前速查手册</Heading>
          <p className={styles.subtitle}>高分速记 · 数字打通 · 高频陷阱标注</p>
        </div>

        <div className={styles.tipBlock}>
          <strong>来源提示：</strong>
          本页按整理时的公开法规和本地第三方练习题高频点归纳，用作临考速记；练习题来自非官方开源题库 DrivingTestSubjectOne，遇到题库、App 或地方口径不一致时，以公安交管现行法规和考试系统为准。
        </div>

        <div className={styles.examBanner}>
          <div className={styles.examBannerItem}>
            <em>100</em>
            <span>满分100分</span>
          </div>
          <div className={styles.examBannerItem}>
            <em>90</em>
            <span>合格分数线</span>
          </div>
          <div className={styles.examBannerItem}>
            <em>45min</em>
            <span>考试时长</span>
          </div>
          <div className={styles.examBannerItem}>
            <em>单选+判断</em>
            <span>题型</span>
          </div>
        </div>

        <nav className={styles.navTabs} role="tablist" aria-label="考前速查分类">
          {TABS.map(tab => (
            <button
              key={tab.id}
              type="button"
              id={`final-review-tab-${tab.id}`}
              role="tab"
              aria-selected={activeTab === tab.id}
              aria-controls="final-review-panel"
              className={`${styles.navTab} ${activeTab === tab.id ? styles.navTabActive : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <section
          id="final-review-panel"
          role="tabpanel"
          aria-labelledby={`final-review-tab-${activeTab}`}
        >
          <ActiveComponent />
        </section>
      </main>
    </Layout>
  );
}
