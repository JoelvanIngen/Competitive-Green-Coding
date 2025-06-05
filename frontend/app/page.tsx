export default function Home() {
  return (
    <div
      className="min-h-screen flex items-start justify-center text-theme-text px-8 py-50
                 bg-gradient-to-r from-[var(--theme-bg)] from-30% via-[#071f12] via-50% to-[#071f12] to-90%"
    >
      {/* Container smaller en gecentreerd */}
      <div className="max-w-4xl w-full flex items-start justify-between relative">
        {/* Linkerkant: tekst en knoppen */}
        <div className="max-w-md flex flex-col gap-6 absolute left-0 -translate-x-16 z-10">
          <h1 className="text-8xl font-bold text-theme-primary">GreenCode</h1>
          <p className="text-xl text-white/90">
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
              href="/"
              className="bg-theme-primary text-white font-semibold px-6 py-3 rounded-lg hover:bg-theme-primary-dark transition"
            >
              Leaderboard
            </a>
          </div>
        </div>

        {/* Rechterkant: afbeelding groter */}
        <div className="flex-shrink-0 px-70 py-20">
          <img
            src="/images/mascotte_greencoding.png"
            alt="Mascotte Greencoding"
            className="max-w-[700px] object-contain"
          />
        </div>
      </div>
    </div>
  );
}
