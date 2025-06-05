export default function Home() {
  return (
    <div className="min-h-screen flex text-theme-text px-8 py-16 bg-gradient-to-r from-[var(--theme-bg)] via-[] to-[#071f12]">
      {/* Linkerkant: tekst */}
      <div className="flex-1 flex flex-col justify-start items-start pt-40 pr-12">
        <h1 className="text-5xl font-bold text-theme-primary mb-6">Greencoding</h1>
        <p className="text-lg max-w-md mb-8">
          Competitive programming against each other where sustainability matters!
        </p>
        <a
          href="/login"
          className="bg-theme-primary text-white font-semibold px-6 py-3 rounded-lg hover:bg-theme-primary-dark transition"
        >
          Start Here
        </a>
      </div>

      {/* Rechterkant: afbeelding */}
      <div className="flex-1 flex justify-center items-start pt-30">
        <img
          src="/images/mascotte_greencoding.png"
          alt="Boze uil"
          className="max-w-full max-h-[400px] object-contain"
        />
      </div>
    </div>
  );
}
