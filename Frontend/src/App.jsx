import { BrowserRouter } from "react-router-dom";
import { ThemeProvider } from "./context/ThemeContext";
import { DocumentProvider } from "./context/DocumentContext";
import { ChatProvider } from "./context/ChatContext";
import { ToastProvider } from "./components/common/Toast";
import AppRoutes from "./routes/AppRoutes";
import LegalBriefApp from "./Legalbriefapp";

export default function App() {
  return (
      <LegalBriefApp/>
    // <ThemeProvider>
    //   <ToastProvider>
    //     <DocumentProvider>
    //       <ChatProvider>
    //         <BrowserRouter>
    //           <AppRoutes />
    //         </BrowserRouter>
    //       </ChatProvider>
    //     </DocumentProvider>
    //   </ToastProvider>
    // </ThemeProvider>
  );
}
