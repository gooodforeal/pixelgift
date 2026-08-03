import { Link } from "react-router-dom";

import { PageTransition } from "../components/PageTransition";

export function NotFoundPage() {
  return (
    <PageTransition>
      <div className="grid min-h-[70dvh] place-items-center text-center">
        <div className="glass max-w-md px-8 py-14">
          <span className="text-5xl">🎈</span>
          <h1 className="font-display mt-6 text-3xl">Страница улетела</h1>
          <p className="mt-3 text-sm text-slate-400">
            Такой страницы нет — возможно, ссылка устарела.
          </p>
          <Link to="/" className="btn-primary mt-8">
            На главную
          </Link>
        </div>
      </div>
    </PageTransition>
  );
}
