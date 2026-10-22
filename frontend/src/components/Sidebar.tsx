import { LayoutGrid, Construction, Waves, Droplets, Lightbulb, MoreHorizontal, AlertTriangle, Flame, Clock, CheckCircle } from 'lucide-react';

interface SidebarProps {
  selectedCategory: string;
  onSelectCategory: (category: string) => void;
  selectedPriority?: string;
  onSelectPriority?: (priority: string) => void;
}

export default function Sidebar({
  selectedCategory,
  onSelectCategory,
  selectedPriority = 'All',
  onSelectPriority
}: SidebarProps) {
  const categories = [
    { name: 'All', icon: LayoutGrid },
    { name: 'Road', icon: Construction },
    { name: 'Drainage', icon: Waves },
    { name: 'Water Supply', icon: Droplets },
    { name: 'Street Lights', icon: Lightbulb },
    { name: 'Others', icon: MoreHorizontal },
  ];

  const priorities = [
    { name: 'All', icon: LayoutGrid, color: 'text-gray-500' },
    { name: 'Critical', icon: Flame, color: 'text-red-500' },
    { name: 'High', icon: AlertTriangle, color: 'text-orange-500' },
    { name: 'Medium', icon: Clock, color: 'text-amber-500' },
    { name: 'Low', icon: CheckCircle, color: 'text-emerald-500' },
  ];

  return (
    <aside className="w-20 md:w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col shrink-0">
      <div className="p-4 space-y-6">
        {/* Civic Wing / Department */}
        <div>
          <h2 className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider mb-3 hidden md:block">
            Municipal Departments
          </h2>
          <nav className="space-y-1.5">
            {categories.map((cat) => {
              const Icon = cat.icon;
              const isActive = selectedCategory.toLowerCase() === cat.name.toLowerCase();
              return (
                <button
                  key={cat.name}
                  onClick={() => onSelectCategory(cat.name)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors text-xs font-semibold ${
                    isActive
                      ? 'bg-teal-50 dark:bg-teal-950/50 text-teal-700 dark:text-teal-300 font-bold border-l-4 border-teal-600 shadow-2xs'
                      : 'text-slate-600 dark:text-gray-400 hover:bg-slate-100 dark:hover:bg-gray-700/50 hover:text-slate-900 dark:hover:text-gray-200'
                  }`}
                  title={cat.name}
                >
                  <Icon size={17} className={isActive ? 'text-teal-600 dark:text-teal-400' : 'text-slate-400'} />
                  <span className="hidden md:inline">{cat.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Priority Filter */}
        {onSelectPriority && (
          <div className="pt-4 border-t border-slate-100 dark:border-gray-700">
            <h2 className="text-[10px] font-bold text-slate-400 dark:text-gray-500 uppercase tracking-wider mb-2 hidden md:block">
              Priority Filter
            </h2>
            <nav className="space-y-1">
              {priorities.map((prio) => {
                const Icon = prio.icon;
                const isActive = selectedPriority.toLowerCase() === prio.name.toLowerCase();
                return (
                  <button
                    key={prio.name}
                    onClick={() => onSelectPriority(prio.name)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors text-xs ${
                      isActive
                        ? 'bg-teal-50 dark:bg-teal-950/50 text-teal-800 dark:text-teal-300 font-bold border-l-2 border-teal-500'
                        : 'text-slate-600 dark:text-gray-400 hover:bg-slate-100 dark:hover:bg-gray-700/50'
                    }`}
                    title={prio.name}
                  >
                    <Icon size={15} className={prio.color} />
                    <span className="hidden md:inline">{prio.name}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        )}


      </div>
    </aside>
  );
}
