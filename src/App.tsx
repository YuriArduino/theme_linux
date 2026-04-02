import { motion } from "motion/react";
import { Terminal, Download, Search, Zap, Github, Package, Info } from "lucide-react";

const FeatureCard = ({ icon: Icon, title, description }: { icon: any, title: string, description: string }) => (
  <motion.div 
    whileHover={{ y: -5 }}
    className="p-6 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm"
  >
    <div className="w-12 h-12 rounded-xl bg-magenta-500/20 flex items-center justify-center mb-4">
      <Icon className="w-6 h-6 text-magenta-400" />
    </div>
    <h3 className="text-xl font-semibold mb-2 text-white">{title}</h3>
    <p className="text-gray-400 leading-relaxed">{description}</p>
  </motion.div>
);

const CommandItem = ({ cmd, desc }: { cmd: string, desc: string }) => (
  <div className="flex items-start gap-4 p-4 rounded-xl bg-black/20 border border-white/5">
    <code className="text-magenta-400 font-mono whitespace-nowrap">{cmd}</code>
    <span className="text-gray-400 text-sm">{desc}</span>
  </div>
);

export default function App() {
  return (
    <div className="min-h-screen bg-[#0a0a0a] text-gray-100 font-sans selection:bg-magenta-500/30">
      {/* Hero Section */}
      <header className="relative overflow-hidden pt-20 pb-32 px-6">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-7xl h-full pointer-events-none">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-magenta-500/10 blur-[120px] rounded-full" />
          <div className="absolute bottom-[10%] right-[-5%] w-[30%] h-[30%] bg-blue-500/10 blur-[100px] rounded-full" />
        </div>

        <div className="max-w-5xl mx-auto relative z-10 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-magenta-500/10 border border-magenta-500/20 text-magenta-400 text-sm font-medium mb-8">
              <Package className="w-4 h-4" />
              <span>v1.0.0 Released</span>
            </div>
            <h1 className="text-6xl md:text-7xl font-bold tracking-tight mb-6 bg-gradient-to-b from-white to-gray-400 bg-clip-text text-transparent">
              themectl
            </h1>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
              A modern, open-source CLI tool for browsing, installing, and managing Linux desktop themes from the OpenDesktop API.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4">
              <button className="px-8 py-4 rounded-xl bg-magenta-600 hover:bg-magenta-500 text-white font-semibold transition-all flex items-center gap-2 shadow-lg shadow-magenta-600/20">
                <Download className="w-5 h-5" />
                Install Now
              </button>
              <button className="px-8 py-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold transition-all flex items-center gap-2">
                <Github className="w-5 h-5" />
                View Source
              </button>
            </div>
          </motion.div>
        </div>
      </header>

      {/* Terminal Preview */}
      <section className="px-6 -mt-20 mb-32">
        <div className="max-w-4xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.8 }}
            className="rounded-2xl border border-white/10 bg-[#121212] shadow-2xl overflow-hidden"
          >
            <div className="flex items-center gap-2 px-4 py-3 bg-[#1a1a1a] border-b border-white/5">
              <div className="w-3 h-3 rounded-full bg-red-500/50" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
              <div className="w-3 h-3 rounded-full bg-green-500/50" />
              <div className="ml-4 text-xs text-gray-500 font-mono">themectl — bash</div>
            </div>
            <div className="p-6 font-mono text-sm leading-relaxed">
              <div className="flex gap-2">
                <span className="text-green-400">$</span>
                <span className="text-white">themectl search gtk catppuccin</span>
              </div>
              <div className="mt-4 text-gray-400">
                Searching themes...
                <br />
                <br />
                <table className="w-full text-left">
                  <thead>
                    <tr className="text-magenta-400 border-b border-white/5">
                      <th className="pb-2">ID</th>
                      <th className="pb-2">Name</th>
                      <th className="pb-2">Author</th>
                      <th className="pb-2">Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td className="pt-2">172839</td>
                      <td className="pt-2 text-cyan-400">Catppuccin GTK</td>
                      <td className="pt-2 text-green-400">catppuccin</td>
                      <td className="pt-2 text-yellow-400">98</td>
                    </tr>
                    <tr>
                      <td>183940</td>
                      <td className="text-cyan-400">Catppuccin Mocha</td>
                      <td className="text-green-400">catppuccin</td>
                      <td className="text-yellow-400">95</td>
                    </tr>
                  </tbody>
                </table>
                <br />
                <div className="flex gap-2">
                  <span className="text-green-400">$</span>
                  <span className="text-white">themectl install 172839</span>
                </div>
                <div className="mt-2 text-blue-400">
                  Downloading Catppuccin GTK... [████████████████] 100%
                </div>
                <div className="text-green-400">
                  Successfully installed to ~/.themes/
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="max-w-6xl mx-auto px-6 mb-32">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">Powerful Theme Management</h2>
          <p className="text-gray-400">Everything you need to customize your Linux desktop experience.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          <FeatureCard 
            icon={Search}
            title="Smart Search"
            description="Find themes instantly using keywords, categories, or ratings directly from the OCS database."
          />
          <FeatureCard 
            icon={Zap}
            title="Fast Installation"
            description="Automatic downloading, extraction, and deployment to your local theme directories."
          />
          <FeatureCard 
            icon={Terminal}
            title="TUI Mode"
            description="Interactive terminal interface for browsing themes with live previews and details."
          />
        </div>
      </section>

      {/* Commands Section */}
      <section className="max-w-4xl mx-auto px-6 mb-32">
        <div className="bg-white/5 border border-white/10 rounded-3xl p-8 md:p-12">
          <div className="flex items-center gap-4 mb-8">
            <div className="p-3 rounded-2xl bg-magenta-500/20">
              <Info className="w-6 h-6 text-magenta-400" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Quick Reference</h2>
              <p className="text-gray-400 text-sm">Common commands to get you started.</p>
            </div>
          </div>
          <div className="grid gap-3">
            <CommandItem cmd="themectl search <query>" desc="Search for themes by keyword" />
            <CommandItem cmd="themectl top" desc="Show top-rated themes" />
            <CommandItem cmd="themectl preview <id>" desc="Show theme details and screenshots" />
            <CommandItem cmd="themectl install <id>" desc="Install a theme to ~/.themes/" />
            <CommandItem cmd="themectl browse" desc="Open interactive TUI browser" />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-magenta-600 flex items-center justify-center font-bold text-white">T</div>
            <span className="font-bold text-xl tracking-tight">themectl</span>
          </div>
          <div className="flex gap-8 text-sm text-gray-500">
            <a href="#" className="hover:text-white transition-colors">Documentation</a>
            <a href="#" className="hover:text-white transition-colors">API Reference</a>
            <a href="#" className="hover:text-white transition-colors">Community</a>
          </div>
          <div className="text-sm text-gray-600">
            © 2026 themectl project. Open Source under MIT.
          </div>
        </div>
      </footer>
    </div>
  );
}
