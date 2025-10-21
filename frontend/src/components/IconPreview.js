import React from 'react';
import {
 Home,
 LayoutDashboard,
 Search,
 Newspaper,
 Briefcase,
 DollarSign,
 Settings,
 Zap,
 History,
 Target,
 Users,
 Eye,
 Activity,
 Award,
 Database,
 BarChart3,
 PieChart,
 Bot,
 Shield,
 CreditCard,
 Globe,
 TrendingUp,
 TrendingDown,
} from 'lucide-react';

const groups = [
 {
 title: 'Home',
 variants: [
 { name: 'Home', Icon: Home },
 { name: 'LayoutDashboard', Icon: LayoutDashboard },
 { name: 'PieChart (alt)', Icon: PieChart },
 ],
 },
 {
 title: 'Stock Search',
 variants: [
 { name: 'Search', Icon: Search },
 { name: 'Database', Icon: Database },
 { name: 'Target (scan)', Icon: Target },
 ],
 },
 {
 title: 'Market News',
 variants: [
 { name: 'Newspaper', Icon: Newspaper },
 { name: 'Globe', Icon: Globe },
 { name: 'Activity (market)', Icon: Activity },
 ],
 },
 {
 title: 'Mindfolios',
 variants: [
 { name: 'Briefcase', Icon: Briefcase },
 { name: 'PieChart', Icon: PieChart },
 { name: 'BarChart3', Icon: BarChart3 },
 ],
 },
 {
 title: 'TradeStation / Auth',
 variants: [
 { name: 'Settings', Icon: Settings },
 { name: 'Shield', Icon: Shield },
 { name: 'CreditCard', Icon: CreditCard },
 ],
 },
 {
 title: 'Account Balance',
 variants: [
 { name: 'DollarSign', Icon: DollarSign },
 { name: 'PieChart', Icon: PieChart },
 { name: 'BarChart3', Icon: BarChart3 },
 ],
 },
 {
 title: 'Options Module',
 variants: [
 { name: 'Zap', Icon: Zap },
 { name: 'Target', Icon: Target },
 { name: 'Settings (advanced)', Icon: Settings },
 ],
 },
 {
 title: 'Puts Options Selling',
 variants: [
 { name: 'Target', Icon: Target },
 { name: 'TrendingUp', Icon: TrendingUp },
 { name: 'TrendingDown', Icon: TrendingDown },
 ],
 },
 {
 title: 'Unusual Whales',
 variants: [
 { name: 'Activity', Icon: Activity },
 { name: 'Eye', Icon: Eye },
 { name: 'Users (insiders)', Icon: Users },
 ],
 },
 {
 title: 'Investment Scoring',
 variants: [
 { name: 'Award', Icon: Award },
 { name: 'Target', Icon: Target },
 { name: 'BarChart3', Icon: BarChart3 },
 ],
 },
 {
 title: 'Auto Options Trading',
 variants: [
 { name: 'Bot', Icon: Bot },
 { name: 'Zap', Icon: Zap },
 { name: 'Activity', Icon: Activity },
 ],
 },
];

const IconCard = ({ Icon, name }) => (
 <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 flex flex-col items-center hover:border-slate-500 transition-colors">
 <div className="w-12 h-12 rounded-lg bg-slate-700 flex items-center justify-center mb-2">
 <Icon size={22} className="text-slate-200" />
 </div>
 <div className="text-lg text-slate-300">{name}</div>
 </div>
);

export default function IconPreview() {
 return (
 <div className="min-h-screen bg-slate-900 text-[rgb(252, 251, 255)] p-6">
 <div className="max-w-6xl mx-auto">
 <div className="mb-6">
 <h1 className="text-2xl font-medium">Icon Preview (temporary)</h1>
 <p className="text-slate-400 text-xl">Alege iconul preferat pentru fiecare secțiune. Pagina este temporară și o voi elimina după selecție.</p>
 </div>

 <div className="space-y-8">
 {groups.map((group, idx) => (
 <div key={idx}>
 <div className="mb-3 text-slate-200 font-medium">{group.title}</div>
 <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
 {group.variants.map((v, i) => (
 <IconCard key={`${group.title}-${i}`} Icon={v.Icon} name={v.name} />
 ))}
 </div>
 </div>
 ))}
 </div>
 </div>
 </div>
 );
}
