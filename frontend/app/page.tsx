import { Card, CardContent } from "@/components/ui/card";

export default function Home() {
  return (
    <div
      className="min-h-screen flex items-start justify-center text-theme-text px-8 py-50
                 bg-gradient-to-r from-[#071f12] from-0% via-[var(--theme-primary)] via-50% to-[#071f12] to-100%"
    >
      {/* Container smaller en gecentreerd */}
      <div className="max-w-5xl w-full flex items-start justify-between ">
        {/* Linkerkant: tekst en knoppen */}
        <div className="flex flex-col -translate-x-20">
          <Card className="w-full shadow-lg">
            <CardContent className="p-6 overflow-x-auto">
              <div className="flex flex-col gap-6">
                <h1 className="text-8xl font-bold text-theme-primary">GreenCode</h1>
                  <p className="text-xl text-theme-text">
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
            </CardContent>
          </Card>
        </div>

        {/* Rechterkant: afbeelding groter */}
        <div className="flex-shrink-0 -translate-x-16">
          <img
            src="/images/raw.png"
            alt="Mascotte Greencoding"
            className="max-w-[300px] object-contain"
          />
        </div>
      </div>
    </div>
  );
}
