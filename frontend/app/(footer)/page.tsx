import { Card, CardContent } from "@/components/ui/card";

export default function Home() {
  return (
    <div
      className="flex-1 text-theme-text px-8 border-t
                 bg-[url('/images/groot_background.png')] bg-cover bg-center"
    >
      <div className="max-w-3xl flex flex-col items-start justify-start py-30">
        <div className="max-w-2xl flex flex-col gap-6">
          <h1 className="text-4xl sm:text-6xl md:text-7xl lg:text-8xl font-bold text-theme-primary -translate-x-1.5">
            GreenCode
          </h1>
          <p className="text-xl text-white">
            GreenCode is a platform where developers can test their sustainable programming skills.
            Take on different challenges and compete with others on our leaderboards.
            Your journey for writing green code starts here!
          </p>
          <div className="flex gap-6">
            <a
              href="/login"
              className="bg-theme-primary text-white font-semibold px-6 py-3
                         rounded-lg hover:bg-theme-primary-dark transition"
            >
              Start Here
            </a>
            <a
              href="/help"
              className="bg-theme-primary text-white font-semibold px-6 py-3
                         rounded-lg hover:bg-theme-primary-dark transition"
            >
              Learn More
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
