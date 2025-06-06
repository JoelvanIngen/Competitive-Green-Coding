import { Card, CardContent } from "@/components/ui/card";

export default function Home() {
  return (
    <div
      className="min-h-screen flex items-start justify-center text-theme-text px-8 py-30 border-t
                 bg-[url('/images/groot_background.png')] bg-cover bg-center"
    >
      <div className="max-w-5xl w-full flex items-start justify-between ">
        {/* Linkerkant: tekst en knoppen */}
        <div className="max-w-2xl flex flex-col -translate-x-30">
              <div className="flex flex-col gap-6">
                <h1 className="text-8xl font-bold text-theme-primary">GreenCode</h1>
                  <p className="text-xl text-white">
                    GreenCode is a platform where developers can test their sustainable programming skills. Take on different challenges and compete with others on our leaderboards. Your journey for writing green code starts here!
                  </p>
                <div className="flex gap-6">
                  <a
                    href="/login"
                    className="bg-theme-primary text-white font-semibold px-6 py-3 rounded-lg hover:bg-theme-primary-dark transition"
                  >
                    Start Here
                  </a>
                  <a
                    href="/leaderboards"
                    className="bg-theme-primary text-white font-semibold px-6 py-3 rounded-lg hover:bg-theme-primary-dark transition"
                  >
                    Leaderboard
                  </a>
                </div>
              </div>
        </div>

        {/* Rechterkant */}
        {/* <div className="flex-shrink-0 -translate-x-16">
          <img
            src="/images/raw.png"
            alt="Mascotte Greencoding"
            className="max-w-[290px] object-contain"
          />
        </div> */}
      </div>
    </div>
  );
}
