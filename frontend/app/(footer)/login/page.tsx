// import { LoginWidget } from "@/app/login/login-widget";
import { LoginWidget } from "./login-widget";

export default function LoginPage() {
  return (
    /* Large padding for top and bottom, small margins at the sides. */
    <div className="pt-16 pb-16 mx-8">
      <LoginWidget />
    </div>
  );
}
