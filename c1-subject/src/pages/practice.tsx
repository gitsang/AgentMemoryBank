import {useState} from 'react';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import questions from '../../data/processed/questions.json';

type Question = {
  id: string;
  subject?: string;
  chapter_id?: string;
  question: string;
  options: string[];
  answer: string;
  answer_text?: string;
  answer_skill?: string;
  tags?: string[];
  topic?: string;
  subtopic?: string;
  question_type?: string;
  image_url?: string;
};

const subjectQuestions = (questions as Question[]).filter(
  (item) => item.subject === '1' && item.question,
);

const answerLetters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

const labelForOption = (option: string, optionIndex: number) => {
  if (option === '正确' || option === '错误') {
    return option;
  }
  return `${answerLetters[optionIndex]}. ${option}`;
};

const isCorrect = (question: Question, choice: string) => {
  if (question.question_type === 'true_false') {
    return choice === question.answer || choice === question.answer_text;
  }

  return choice === question.answer;
};

export default function PracticePage() {
  const [practiceQuestions, setPracticeQuestions] = useState(subjectQuestions);
  const [index, setIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [score, setScore] = useState({correct: 0, wrong: 0});
  const [revealText, setRevealText] = useState('');

  if (subjectQuestions.length === 0) {
    return (
      <Layout title="Practice" description="Subject 1 practice questions">
        <main className="container margin-vert--xl">
          <Heading as="h1">Practice</Heading>
          <p>No subject 1 questions were found in the local dataset.</p>
        </main>
      </Layout>
    );
  }

  const current = practiceQuestions[index];

  const nextQuestion = () => {
    setShowAnswer(false);
    setRevealText('');
    setIndex((value) => (value + 1) % practiceQuestions.length);
  };

  const shuffleQuestions = () => {
    setPracticeQuestions([...subjectQuestions].sort(() => Math.random() - 0.5));
    setIndex(0);
    setShowAnswer(false);
    setRevealText('');
    setScore({correct: 0, wrong: 0});
  };

  const answerWith = (choice: string) => {
    if (isCorrect(current, choice)) {
      setScore((value) => ({...value, correct: value.correct + 1}));
    } else {
      setScore((value) => ({...value, wrong: value.wrong + 1}));
    }
    setRevealText(choice);
    setShowAnswer(true);
  };

  return (
    <Layout title="Practice" description="Subject 1 practice questions">
      <main className="container margin-vert--xl">
        <div className="row">
          <div className="col col--10 col--offset-1">
            <Heading as="h1">Practice</Heading>
            <p>
              Subject 1 questions from the normalized local dataset. Quiz mode
              first.
            </p>
            <button className="button button--outline button--primary margin-bottom--md" onClick={shuffleQuestions}>
              Shuffle questions
            </button>

            <div className="card margin-bottom--md">
              <div className="card__body">
                <strong>
                  {index + 1} / {practiceQuestions.length}
                </strong>
                <p>{current.question}</p>
                {current.image_url ? (
                  <img
                    alt="Question illustration"
                    src={current.image_url}
                    style={{maxWidth: '100%', borderRadius: '0.75rem', marginBottom: '1rem'}}
                  />
                ) : null}

                {showAnswer ? (
                  <div>
                    <p>
                      <strong>Your choice:</strong> {revealText}
                    </p>
                    <p>
                      <strong>Answer:</strong> {current.answer_text ?? current.answer}
                    </p>
                    {current.answer_skill ? <p>{current.answer_skill}</p> : null}
                    <button className="button button--primary" onClick={nextQuestion}>
                      Next question
                    </button>
                  </div>
                ) : (
                  <div className="button-group button-group--block" style={{flexWrap: 'wrap'}}>
                    {current.options.map((option, optionIndex) => {
                      const choice = current.question_type === 'true_false'
                        ? option
                        : answerLetters[optionIndex];
                      return (
                        <button
                          className="button button--secondary"
                          key={`${current.id}-${choice}`}
                          onClick={() => answerWith(choice)}>
                          {labelForOption(option, optionIndex)}
                        </button>
                      );
                    })}
                    <button className="button button--secondary" onClick={() => setShowAnswer(true)}>
                      Reveal answer
                    </button>
                  </div>
                )}
              </div>
            </div>

            <div className="alert alert--info">
              <strong>Score:</strong> {score.correct} correct / {score.wrong} wrong
            </div>
          </div>
        </div>
      </main>
    </Layout>
  );
}
