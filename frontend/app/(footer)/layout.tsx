import Footer from "@/components/footer"

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex flex-col flex-1">{children}</main>
      <Footer />
    </div>
  );
}
