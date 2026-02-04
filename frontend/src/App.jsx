import React from 'react';
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Services from "./components/Services";
import Experience from "./components/Experience";
import About from "./components/About";
import ChatbotSection from "./components/ChatbotSection";  // ← NUEVO
import Contact from "./components/Contact";
import Footer from "./components/Footer";

const BackgroundEffect = () => (
  <div className="fixed inset-0 -z-10 overflow-hidden bg-darkBg">
    <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-accent/5 blur-[120px]" />
    <div className="absolute bottom-[10%] left-[-5%] w-[40%] h-[40%] rounded-full bg-blue-500/5 blur-[100px]" />
    <div className="absolute inset-0 bg-darkBg/20" />
  </div>
);

function App() {
  return (
    <div className="bg-grain min-h-screen text-textMain selection:bg-accent/30 selection:text-accent font-sans antialiased">
      <BackgroundEffect />
      <Navbar />
      <main>
        <Hero />
        <Services />
        <Experience />
        <About />
        <ChatbotSection />  
        <Contact />
      </main>
      <Footer />
    </div>
  );
}

export default App;