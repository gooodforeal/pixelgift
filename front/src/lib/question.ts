/** Quiz card payload stored in box item metadata. */

export const QUESTION_TEXT_MIN = 3;
export const QUESTION_TEXT_MAX = 50;
export const QUESTION_OPTIONS_MIN = 2;
export const QUESTION_OPTIONS_MAX = 4;
export const QUESTION_OPTION_MAX = 40;

export interface QuestionPayload {
  question: string;
  options: string[];
  correct_index: number;
}

export function questionFromMetadata(
  metadata: Record<string, unknown> | null | undefined,
): QuestionPayload | null {
  if (!metadata) return null;
  const question = metadata.question;
  const options = metadata.options;
  const correct = metadata.correct_index;
  if (typeof question !== "string") return null;
  if (!Array.isArray(options)) return null;
  if (typeof correct !== "number" || !Number.isInteger(correct)) return null;
  const texts = options.filter((item): item is string => typeof item === "string");
  if (texts.length !== options.length) return null;
  if (texts.length < QUESTION_OPTIONS_MIN || texts.length > QUESTION_OPTIONS_MAX) {
    return null;
  }
  if (correct < 0 || correct >= texts.length) return null;
  return {
    question: question.trim(),
    options: texts.map((text) => text.trim()),
    correct_index: correct,
  };
}

export function emptyQuestionDraft(): {
  question: string;
  options: string[];
  correctIndex: number;
} {
  return {
    question: "",
    options: ["", ""],
    correctIndex: 0,
  };
}
