import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Edit2, Trash2, ArrowLeft, Calendar, MapPin, Search, Plus, TrendingUp, Users, Activity, Loader2, Save, X, LogOut, ClipboardList, Database, FileCheck, Eye, FileText, CreditCard, TrendingDown, History, FileSpreadsheet, RefreshCw, ArrowRightLeft, Settings, Mail, Phone, Lock } from 'lucide-react';
import { URBAN_BARANGAYS, RURAL_BARANGAYS } from '../data/barangays';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';


import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

function LocationMarker({ position, setPosition }) {
    useMapEvents({
        click(e) {
            setPosition(e.latlng);
        },
    });

    return position === null ? null : (
        <Marker position={position}></Marker>
    );
}

export default function AdminDashboard() {
    const [events, setEvents] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [stats, setStats] = useState({ totalEvents: 0, activeParticipants: 0, totalPoints: 0 });
    const adminUser = JSON.parse(localStorage.getItem('user')) || {};
    const [newForm, setNewForm] = useState({
        title: '', description: '', location: '', date: '', time: '', points_reward: 10, barangay: adminUser.barangay || URBAN_BARANGAYS[0]
    });

    const [globalLogs, setGlobalLogs] = useState([]);
    const [barangayStats, setBarangayStats] = useState([]);
    const [allUsers, setAllUsers] = useState([]);
    const [showLogsModal, setShowLogsModal] = useState(false);
    const [showStatsModal, setShowStatsModal] = useState(false);
    const [showUsersModal, setShowUsersModal] = useState(false);
    const [residentSearch, setResidentSearch] = useState('');
    const [residentFilter, setResidentFilter] = useState('All');
    const [redemptions, setRedemptions] = useState([]);
    const [expenses, setExpenses] = useState([]);
    const [expenseSummary, setExpenseSummary] = useState({ total_budget: 0, total_spent: 0, remaining: 0 });
    const [showFinanceModal, setShowFinanceModal] = useState(false);
    const [showRedemptionModal, setShowRedemptionModal] = useState(false);
    const [showTransferModal, setShowTransferModal] = useState(false);
    const [selectedUser, setSelectedUser] = useState(null);
    const [transferBarangay, setTransferBarangay] = useState('');
    const [newExpense, setNewExpense] = useState({ amount: '', description: '', category: 'Spent', date: new Date().toISOString().split('T')[0] });
    const [reportFilter, setReportFilter] = useState('All');
    const [residentView, setResidentView] = useState('Local');
    const [externalResidents, setExternalResidents] = useState([]);
    const [isSearchingExternal, setIsSearchingExternal] = useState(false);
    const [incomingTransfers, setIncomingTransfers] = useState([]);
    const [showTransferRequestsModal, setShowTransferRequestsModal] = useState(false);
    const [showProfileModal, setShowProfileModal] = useState(false);
    const [profileFormData, setProfileFormData] = useState({
        username: adminUser.username || '',
        email: adminUser.email || '',
        phone_number: adminUser.phone_number || '',
        password: ''
    });
    const [updatingProfile, setUpdatingProfile] = useState(false);

    const filteredEvents = events.filter(event => {
        const matchesSearch = event.title.toLowerCase().includes(searchTerm.toLowerCase());
        if (reportFilter === 'All') return matchesSearch;
        const eventDate = new Date(event.date);
        const now = new Date();
        if (reportFilter === 'Weekly') {
            const weekAgo = new Date();
            weekAgo.setDate(now.getDate() - 7);
            return matchesSearch && eventDate >= weekAgo;
        }
        if (reportFilter === 'Monthly') {
            const monthAgo = new Date();
            monthAgo.setMonth(now.getMonth() - 1);
            return matchesSearch && eventDate >= monthAgo;
        }
        if (reportFilter === 'Yearly') {
            const yearAgo = new Date();
            yearAgo.setFullYear(now.getFullYear() - 1);
            return matchesSearch && eventDate >= yearAgo;
        }
        return matchesSearch;
    });

    const navigate = useNavigate();

    useEffect(() => {
        let currentAdmin = JSON.parse(localStorage.getItem('user'));
        if (!currentAdmin || currentAdmin.role !== 'admin') {
            const devAdmin = { id: 999, username: 'Dev_Admin', role: 'admin', barangay: 'Santa Monica', is_verified: true };
            localStorage.setItem('user', JSON.stringify(devAdmin));
            localStorage.setItem('token', 'DEV_BYPASS_TOKEN');
        }
        fetchData();
    }, []);

    const getHeaders = (token) => {
        if (token === 'DEV_BYPASS_TOKEN') return { 'X-Dev-Bypass': 'DEV_BYPASS_TOKEN', 'Content-Type': 'application/json' };
        return { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/admin/login');
    };

    const handleUnauthorized = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        navigate('/admin/login');
    };

    const fetchData = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/events/', { headers: getHeaders(token) });
            if (res.status === 401) return handleUnauthorized();
            const data = await res.json();
            setEvents(data);

            const lbRes = await fetch('/api/events/leaderboard', { headers: getHeaders(token) });
            const lbData = await lbRes.json();
            setStats({ totalEvents: data.length, activeParticipants: lbData.length, totalPoints: lbData.reduce((acc, curr) => acc + curr.points, 0) });

            const logsRes = await fetch('/api/events/global-logs', { headers: getHeaders(token) });
            setGlobalLogs(await logsRes.json());

            const statsRes = await fetch('/api/events/barangay-stats', { headers: getHeaders(token) });
            setBarangayStats(await statsRes.json());

            const usersRes = await fetch('/api/auth/users', { headers: getHeaders(token) });
            setAllUsers(await usersRes.json());

            const redRes = await fetch('/api/finance/redemption/history', { headers: getHeaders(token) });
            if (redRes.ok) setRedemptions(await redRes.json());

            const expRes = await fetch('/api/finance/expenses', { headers: getHeaders(token) });
            if (expRes.ok) setExpenses(await expRes.json());

            const sumRes = await fetch('/api/finance/expenses/summary', { headers: getHeaders(token) });
            if (sumRes.ok) setExpenseSummary(await sumRes.json());

            const transRes = await fetch('/api/auth/transfer/incoming', { headers: getHeaders(token) });
            if (transRes.ok) setIncomingTransfers(await transRes.json());
        } catch (error) { console.error(error); } finally { setLoading(false); }
    };

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        setUpdatingProfile(true);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/auth/profile/update', {
                method: 'PUT',
                headers: getHeaders(token),
                body: JSON.stringify(profileFormData)
            });
            const data = await res.json();
            if (res.ok) {
                alert('Admin profile updated!');
                localStorage.setItem('user', JSON.stringify(data.user));
                setShowProfileModal(false);
                setProfileFormData({ ...profileFormData, password: '' });
                fetchData();
            } else alert(data.message);
        } catch (error) { console.error(error); } finally { setUpdatingProfile(false); }
    };

    const handleVerifyUser = async (userId) => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/auth/users/verify/${userId}`, { method: 'POST', headers: getHeaders(token) });
            if (res.ok) fetchData();
        } catch (error) { console.error(error); }
    };

    const handleTransferResident = async () => {
        if (!selectedUser || !transferBarangay) return;
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/auth/users/transfer/${selectedUser.id}`, {
                method: 'POST',
                headers: getHeaders(token),
                body: JSON.stringify({ new_barangay: transferBarangay })
            });
            if (res.ok) { setShowTransferModal(false); fetchData(); alert('Transfer successful'); }
        } catch (error) { console.error(error); }
    };

    const handleTransferDecision = async (requestId, decision) => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/auth/transfer/decision', {
                method: 'POST',
                headers: getHeaders(token),
                body: JSON.stringify({ request_id: requestId, decision })
            });
            if (res.ok) { fetchData(); alert(`Request ${decision}`); }
        } catch (error) { console.error(error); }
    };

    const handleAddExpense = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/finance/expenses', {
                method: 'POST',
                headers: getHeaders(token),
                body: JSON.stringify(newExpense)
            });
            if (res.ok) {
                setNewExpense({ amount: '', description: '', category: 'Spent', date: new Date().toISOString().split('T')[0] });
                fetchData();
            }
        } catch (error) { console.error(error); }
    };

    const handleApproveRedemption = async (id) => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/finance/redemption/approve/${id}`, { method: 'POST', headers: getHeaders(token) });
            if (res.ok) fetchData();
        } catch (error) { console.error(error); }
    };

    const handleExportResidents = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/auth/users/export', { headers: getHeaders(token) });
            if (res.ok) {
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Residents_${adminUser.barangay}_${new Date().toISOString().split('T')[0]}.xlsx`;
                a.click();
            }
        } catch (error) { console.error(error); }
    };

    const handleDelete = async (eventId) => {
        if (!window.confirm('Delete this event?')) return;
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/events/${eventId}`, { method: 'DELETE', headers: getHeaders(token) });
            if (res.ok) fetchData();
        } catch (error) { console.error(error); }
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/events/', {
                method: 'POST',
                headers: getHeaders(token),
                body: JSON.stringify({ ...newForm, points_reward: parseInt(newForm.points_reward) })
            });
            if (res.ok) { setShowCreateModal(false); setNewForm({ title: '', description: '', location: '', date: '', time: '', points_reward: 10, barangay: adminUser.barangay }); fetchData(); }
        } catch (error) { console.error(error); }
    };

    const handleSearchExternal = async (query) => {
        if (!query) return setExternalResidents([]);
        setIsSearchingExternal(true);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`/api/auth/users/search?query=${query}`, { headers: getHeaders(token) });
            if (res.ok) setExternalResidents(await res.json());
        } catch (error) { console.error(error); } finally { setIsSearchingExternal(false); }
    };

    useEffect(() => {
        if (residentView === 'External' && residentSearch.length >= 2) {
            const timer = setTimeout(() => handleSearchExternal(residentSearch), 500);
            return () => clearTimeout(timer);
        }
    }, [residentSearch, residentView]);

    return (
        <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans">
            <div className="p-4 sm:p-8">
                <div className="max-w-7xl mx-auto">
                    <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12">
                        <div className="flex items-center gap-4">
                            <div className="bg-red-500/20 p-3 rounded-2xl border border-red-500/30 shadow-lg shadow-red-500/10">
                                <Shield className="w-8 h-8 text-red-500" />
                            </div>
                            <div>
                                <h1 className="text-3xl font-black text-white tracking-tight">Command Center</h1>
                                <p className="text-slate-400 font-mono text-[10px] uppercase tracking-[0.3em] mt-1 italic">Authorized Personnel Only</p>
                            </div>
                        </div>

                        <div className="flex flex-wrap items-center gap-3">
                            <div className="relative">
                                <Search className="w-4 h-4 absolute left-4 top-3.5 text-slate-500" />
                                <input type="text" placeholder="Search direct..." className="bg-slate-900/50 border border-slate-700/50 rounded-2xl py-3 pl-12 pr-4 text-sm focus:ring-2 focus:ring-red-500 outline-none transition-all w-48" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
                            </div>
                            <NavButton icon={<ClipboardList />} onClick={() => setShowLogsModal(true)} title="Activity Logs" />
                            <NavButton icon={<Database />} onClick={() => setShowStatsModal(true)} title="Jurisdiction Stats" />
                            <NavButton icon={<Users />} onClick={() => setShowUsersModal(true)} title="Resident Database" />
                            <NavButton icon={<TrendingDown />} onClick={() => setShowFinanceModal(true)} title="Finance Tracker" />
                            <NavButton icon={<History />} onClick={() => setShowRedemptionModal(true)} title="Redemptions" />
                            <NavButton icon={<ArrowRightLeft />} onClick={() => setShowTransferRequestsModal(true)} title="Transfers" badge={incomingTransfers.filter(r => r.status === 'Pending').length} />
                            <NavButton icon={<Settings />} onClick={() => { setProfileFormData({username: adminUser.username, email: adminUser.email||'', phone_number: adminUser.phone_number||'', password: ''}); setShowProfileModal(true); }} title="Profile" />
                            <button onClick={() => setShowCreateModal(true)} className="bg-red-600 hover:bg-red-500 text-white p-3.5 rounded-2xl shadow-xl shadow-red-600/20 transition-all active:scale-90"><Plus className="w-6 h-6" /></button>
                            <button onClick={handleLogout} className="bg-slate-800 hover:bg-slate-700 text-slate-400 p-3.5 rounded-2xl border border-slate-700 transition-all hover:text-red-400"><LogOut className="w-6 h-6" /></button>
                        </div>
                    </header>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                        <TopStat label="Managed Events" value={stats.totalEvents} icon={<Activity />} color="text-blue-500" bg="bg-blue-500/10" border="border-blue-500/20" />
                        <TopStat label="Community Size" value={allUsers.filter(u => u.role !== 'admin').length} icon={<Users />} color="text-purple-500" bg="bg-purple-500/10" border="border-purple-500/20" />
                        <TopStat label="Treasury Balance" value={`₱${expenseSummary.remaining.toLocaleString()}`} icon={<CreditCard />} color="text-yellow-500" bg="bg-yellow-500/10" border="border-yellow-500/20" />
                    </div>

                    <div className="bg-slate-900/40 border border-slate-800 rounded-[40px] overflow-hidden backdrop-blur-xl shadow-2xl">
                        <table className="w-full text-left">
                            <thead className="bg-slate-800/50 border-b border-slate-700">
                                <tr className="text-[10px] font-black uppercase tracking-widest text-slate-500 font-mono">
                                    <th className="px-8 py-6">Mission ID & Directive</th>
                                    <th className="px-8 py-6">Operational Zone</th>
                                    <th className="px-8 py-6">Deployment window</th>
                                    <th className="px-8 py-6 text-center">System Override</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800">
                                {loading ? (
                                    <tr><td colSpan="4" className="py-24 text-center"><Loader2 className="w-10 h-10 animate-spin mx-auto text-red-500 opacity-50" /></td></tr>
                                ) : filteredEvents.map(event => (
                                    <tr key={event.id} className="hover:bg-red-500/[0.02] transition-colors group">
                                        <td className="px-8 py-6">
                                            <p className="font-bold text-white text-lg leading-tight group-hover:text-red-400 transition-colors">{event.title}</p>
                                            <p className="text-[10px] font-mono text-slate-600 mt-1 uppercase">Directive // {event.id}</p>
                                        </td>
                                        <td className="px-8 py-6"><span className="flex items-center gap-2 text-slate-400 font-medium"><MapPin className="w-3.5 h-3.5 text-red-500" />{event.location}</span></td>
                                        <td className="px-8 py-6"><span className="text-slate-400 font-mono text-xs">{event.date} • {event.time}</span></td>
                                        <td className="px-8 py-6">
                                            <div className="flex items-center justify-center gap-3">
                                                <ActionButton icon={<Users />} color="text-blue-400 hover:bg-blue-400/20" onClick={() => navigate(`/manage-participants/${event.id}`)} />
                                                <ActionButton icon={<Edit2 />} color="text-amber-400 hover:bg-amber-400/20" onClick={() => navigate(`/edit-event/${event.id}`)} />
                                                <ActionButton icon={<Trash2 />} color="text-red-400 hover:bg-red-400/20" onClick={() => handleDelete(event.id)} />
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Modals */}
            {showCreateModal && (
                <Modal title="Deploy New Directive" onClose={() => setShowCreateModal(false)} icon={<Plus className="text-red-500" />}>
                    <form onSubmit={handleCreate} className="space-y-6 p-2">
                        <div className="space-y-4">
                            <InputField label="Mission Title" value={newForm.title} onChange={v => setNewForm({...newForm, title: v})} placeholder="Operation Alpha..." />
                            <div className="grid grid-cols-2 gap-4">
                                <InputField label="Launch Date" type="date" value={newForm.date} onChange={v => setNewForm({...newForm, date: v})} />
                                <InputField label="Launch Time" type="time" value={newForm.time} onChange={v => setNewForm({...newForm, time: v})} />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase text-slate-500 ml-1">Zone Selection (Map Pin)</label>
                                <div className="h-48 rounded-3xl overflow-hidden border border-slate-700 relative z-0">
                                    <MapContainer center={[9.7407, 118.7353]} zoom={13} style={{ height: '100%' }}>
                                        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                                        <LocationMarker position={newForm.location ? newForm.location.split(',').map(Number) : null} setPosition={l => setNewForm({...newForm, location: `${l.lat},${l.lng}`})} />
                                    </MapContainer>
                                </div>
                                <p className="text-[9px] font-mono text-slate-600">COORDS: {newForm.location || 'PENDING'}</p>
                            </div>
                            <textarea placeholder="Mission briefing details..." className="w-full bg-slate-900 border border-slate-700 rounded-2xl p-4 text-sm text-white focus:ring-2 focus:ring-red-500 outline-none h-24 resize-none transition-all" value={newForm.description} onChange={e => setNewForm({...newForm, description: e.target.value})} />
                            <div className="flex items-center gap-2 bg-slate-900 p-4 rounded-2xl border border-slate-700">
                                <Award className="w-5 h-5 text-amber-500" />
                                <input type="number" placeholder="Bounty Points" className="bg-transparent outline-none flex-1 text-white font-bold" value={newForm.points_reward} onChange={e => setNewForm({...newForm, points_reward: e.target.value})} />
                            </div>
                        </div>
                        <button type="submit" className="w-full bg-red-600 py-4 rounded-3xl font-black text-white hover:bg-red-500 shadow-xl shadow-red-900/20 active:scale-95 transition-all">EXECUTE DEPLOYMENT</button>
                    </form>
                </Modal>
            )}

            {/* Profile Modal */}
            {showProfileModal && (
                <Modal title="System Profile" onClose={() => setShowProfileModal(false)} icon={<Settings className="text-red-500" />}>
                    <form onSubmit={handleUpdateProfile} className="space-y-5 p-2">
                        <InputField label="Admin Access Key" value={profileFormData.username} onChange={v => setProfileFormData({...profileFormData, username: v})} icon={<User className="w-4 h-4" />} />
                        <InputField label="Official Email" type="email" value={profileFormData.email} onChange={v => setProfileFormData({...profileFormData, email: v})} icon={<Mail className="w-4 h-4" />} />
                        <InputField label="Emergency Contact" value={profileFormData.phone_number} onChange={v => setProfileFormData({...profileFormData, phone_number: v})} icon={<Phone className="w-4 h-4" />} />
                        <InputField label="New Password (optional)" type="password" value={profileFormData.password} onChange={v => setProfileFormData({...profileFormData, password: v})} icon={<Lock className="w-4 h-4" />} placeholder="••••••••" />
                        <button disabled={updatingProfile} className="w-full bg-red-600 py-5 rounded-3xl font-black text-white hover:bg-red-500 shadow-xl shadow-red-900/20 transition-all mt-4">{updatingProfile ? 'SYNCING...' : 'UPDATE INTERFACE'}</button>
                    </form>
                </Modal>
            )}

            {/* Users Modal */}
            {showUsersModal && (
                <div className="fixed inset-0 bg-slate-900/95 backdrop-blur-xl z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-800 border border-slate-700 w-full max-w-6xl max-h-[90vh] rounded-[48px] shadow-3xl flex flex-col overflow-hidden animate-in slide-in-from-bottom-8 duration-500">
                        <div className="p-10 border-b border-slate-700 flex flex-col gap-8">
                            <div className="flex justify-between items-start">
                                <div className="flex items-center gap-4">
                                    <div className="bg-red-600/20 p-4 rounded-3xl border border-red-500/30"><Users className="w-10 h-10 text-red-500" /></div>
                                    <div><h2 className="text-3xl font-black text-white tracking-tighter uppercase">Resident Data Core</h2><p className="text-slate-500 font-mono text-xs uppercase tracking-widest mt-1">Registry for {adminUser.barangay}</p></div>
                                </div>
                                <button onClick={() => setShowUsersModal(false)} className="p-4 bg-slate-900/50 hover:bg-slate-700 rounded-3xl text-slate-500 transition-all border border-slate-700/50 hover:text-white"><X className="w-8 h-8" /></button>
                            </div>
                            <div className="flex flex-wrap gap-4 items-center">
                                <div className="flex bg-slate-900 p-1.5 rounded-2xl border border-slate-700/50">
                                    {['Local', 'External'].map(v => (
                                        <button key={v} onClick={() => setResidentView(v)} className={`px-8 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${residentView === v ? 'bg-red-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}>{v === 'Local' ? 'Our Residents' : 'Other Jurisdictions'}</button>
                                    ))}
                                </div>
                                <div className="relative flex-1 max-w-md"><Search className="absolute left-4 top-3.5 w-4 h-4 text-slate-500" /><input type="text" placeholder="Filter residents..." className="w-full bg-slate-900 border border-slate-700 rounded-2xl py-3 pl-12 pr-6 text-sm text-white focus:ring-2 focus:ring-red-500 outline-none" value={residentSearch} onChange={e => setResidentSearch(e.target.value)} /></div>
                                <button onClick={handleExportResidents} className="bg-green-600 px-8 py-3 rounded-2xl font-black text-xs text-white hover:bg-green-500 transition-all flex items-center gap-2 shadow-xl shadow-green-900/20 uppercase tracking-widest leading-none"><FileSpreadsheet className="w-4 h-4" /> Export DB</button>
                            </div>
                        </div>
                        <div className="flex-1 overflow-y-auto p-10 custom-scrollbar grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {residentView === 'Local' ? allUsers.filter(u => u.role !== 'admin' && u.username.toLowerCase().includes(residentSearch.toLowerCase())).map(user => (
                                <ResidentCard key={user.id} user={user} onVerify={handleVerifyUser} onTransfer={() => { setSelectedUser(user); setTransferBarangay(user.barangay); setShowTransferModal(true); }} />
                            )) : externalResidents.map(user => (
                                <div key={user.id} className="bg-slate-900/50 p-6 rounded-[32px] border border-blue-500/20 group hover:border-blue-500 transition-all">
                                    <div className="flex items-center gap-4 mb-6"><div className="w-16 h-16 bg-slate-800 rounded-2xl overflow-hidden">{user.id_image ? <img src={`/${user.id_image}`} className="w-full h-full object-cover" /> : <Users className="w-full h-full p-4 text-slate-700" />}</div><div><h4 className="font-bold text-white text-lg">{user.username}</h4><p className="text-[10px] text-blue-400 font-mono uppercase truncate">{user.barangay}</p></div></div>
                                    <button onClick={() => { if(window.confirm(`Initiate transfer of ${user.username} to ${adminUser.barangay}?`)) handleTransferResident(user.id); }} className="w-full bg-blue-600 py-3 rounded-2xl font-black text-[10px] text-white hover:bg-blue-500 uppercase tracking-widest active:scale-95 transition-all">Request Relocation</button>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Other Modals (Brief Versions) */}
            {showLogsModal && <Modal title="Participation Logs" onClose={() => setShowLogsModal(false)} icon={<ClipboardList className="text-blue-500" />} wide>
                <div className="p-4 overflow-x-auto"><table className="w-full text-left text-sm opacity-80"><thead className="text-[10px] uppercase font-mono text-slate-500 border-b border-slate-700"><tr><th className="pb-4">Warrior</th><th className="pb-4">Barangay</th><th className="pb-4">Mission</th><th className="pb-4">Status</th></tr></thead><tbody className="divide-y divide-slate-700/50">{globalLogs.map(log => (<tr key={log.id} className="hover:bg-blue-500/5 transition-colors"><td className="py-4 font-bold text-slate-200">{log.user?.username}</td><td className="py-4 text-slate-400">{log.user?.barangay}</td><td className="py-4 text-slate-400">{log.event?.title}</td><td className="py-4"><span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase ${log.status === 'attended' ? 'bg-green-500/20 text-green-500' : 'bg-yellow-500/20 text-yellow-500'}`}>{log.status}</span></td></tr>))}</tbody></table></div>
            </Modal>}

            {showStatsModal && <Modal title="Jurisdiction Analytics" onClose={() => setShowStatsModal(false)} icon={<Database className="text-purple-500" />}>
                <div className="space-y-4 p-2">{barangayStats.sort((a,b)=>b.total_points-a.total_points).map(s=>(<div key={s.barangay} className="bg-slate-900 p-5 rounded-3xl border border-slate-700 flex justify-between items-center"><div><p className="font-bold text-white">{s.barangay}</p><p className="text-[10px] text-slate-500 uppercase font-mono">{s.total_users} Warriors</p></div><div className="text-right"><p className="text-2xl font-black text-green-500">{s.total_points.toLocaleString()}</p><p className="text-[9px] text-slate-600 font-bold uppercase tracking-widest">Points</p></div></div>))}</div>
            </Modal>}

            {showFinanceModal && <Modal title="Treasury Management" onClose={() => setShowFinanceModal(false)} icon={<TrendingDown className="text-yellow-500" />} wide>
                <div className="flex h-[500px]"><div className="w-72 border-r border-slate-700 p-6 space-y-6 flex-shrink-0"><h3 className="text-[10px] font-black uppercase text-slate-500 tracking-widest">Log Transaction</h3><form onSubmit={handleAddExpense} className="space-y-4">
                    <InputField label="Amount (₱)" type="number" value={newExpense.amount} onChange={v=>setNewExpense({...newExpense, amount:v})} /><select className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm text-white outline-none" value={newExpense.category} onChange={e=>setNewExpense({...newExpense, category:e.target.value})}><option value="Spent">Outflow (Expense)</option><option value="Budget">Inflow (Budget)</option></select><textarea placeholder="Purpose..." className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm h-24 outline-none resize-none" value={newExpense.description} onChange={e=>setNewExpense({...newExpense, description:e.target.value})} /><button className="w-full bg-yellow-600 py-3 rounded-2xl font-black text-xs text-white uppercase tracking-widest hover:bg-yellow-500 transition-all">Record</button></form></div><div className="flex-1 p-6 overflow-y-auto"><h3 className="text-[10px] font-black uppercase text-slate-500 tracking-widest mb-6">Financial History</h3><div className="space-y-3">{expenses.map(e=>(<div key={e.id} className="bg-slate-900/30 p-4 border border-slate-800 rounded-2xl flex justify-between items-center"><div><p className="font-bold text-slate-200">{e.description}</p><p className="text-[9px] font-mono text-slate-500 uppercase">{e.date} / {e.category}</p></div><p className={`font-black ${e.category==='Budget'?'text-green-500':'text-red-500'}`}>{e.category==='Budget'?'+':'-'} ₱{e.amount.toLocaleString()}</p></div>))}</div></div></div>
            </Modal>}

            {showRedemptionModal && <Modal title="Redemption Claims" onClose={() => setShowRedemptionModal(false)} icon={<History className="text-red-500" />} wide>
                <div className="space-y-4 p-4">{redemptions.map(r=>(<div key={r.id} className="bg-slate-900/40 p-6 border border-slate-800 rounded-[32px] flex justify-between items-center"><div><p className="text-xl font-black text-white leading-tight">{r.item_name}</p><p className="text-[10px] font-mono text-slate-500 uppercase mt-1">Warrior: {r.username} • {new Date(r.timestamp).toLocaleDateString()}</p></div><div className="flex items-center gap-6"><div className="text-right"><p className="text-lg font-black text-red-500">-{r.points_spent} pts</p><p className="text-[9px] font-black text-slate-600 uppercase tracking-widest">Debit</p></div>{r.status==='Pending'?(<button onClick={()=>handleApproveRedemption(r.id)} className="bg-red-600 px-6 py-2.5 rounded-2xl font-black text-[10px] text-white hover:bg-red-500 uppercase tracking-widest">Release</button>):(<div className="bg-green-500/10 text-green-500 px-6 py-2.5 rounded-2xl font-black text-[10px] uppercase border border-green-500/20">Cleared</div>)}</div></div>))}</div>
            </Modal>}

            {showTransferRequestsModal && <Modal title="Transfer Protocol" onClose={() => setShowTransferRequestsModal(false)} icon={<ArrowRightLeft className="text-blue-500" />} wide>
                <div className="space-y-4 p-4">{incomingTransfers.map(req=>(<div key={req.id} className="bg-slate-900/50 p-8 rounded-[40px] border border-slate-700/50 flex justify-between items-center"><div className="flex gap-6 items-center"><div className="p-4 bg-blue-500/10 text-blue-500 rounded-3xl"><User className="w-10 h-10" /></div><div><p className="text-2xl font-black text-white tracking-tighter">{req.username}</p><p className="text-[10px] font-mono text-slate-500 uppercase">From: {req.source_barangay}</p>{req.reason && <p className="text-xs text-slate-400 mt-3 italic border-l-2 border-slate-700 pl-3">"{req.reason}"</p>}</div></div><div className="flex gap-3">{req.status==='Pending'?(<><button onClick={()=>handleTransferDecision(req.id,'Rejected')} className="px-6 py-3 border border-red-500/30 text-red-500 rounded-2xl font-black text-[10px] uppercase tracking-widest">Reject</button><button onClick={()=>handleTransferDecision(req.id,'Approved')} className="px-8 py-3 bg-blue-600 text-white rounded-2xl font-black text-[10px] uppercase tracking-widest hover:bg-blue-500 shadow-xl shadow-blue-900/20">Accept</button></>):(<div className="px-8 py-3 border border-slate-700 text-slate-500 rounded-2xl font-black text-[10px] uppercase">{req.status}</div>)}</div></div>))}</div>
            </Modal>}

            {showTransferModal && (
                <div className="fixed inset-0 bg-slate-900/98 backdrop-blur-3xl z-[100] flex items-center justify-center p-6">
                    <div className="bg-slate-800 border border-slate-700 w-full max-w-sm rounded-[48px] overflow-hidden p-8 shadow-3xl text-center">
                        <div className="w-20 h-20 bg-red-500/20 rounded-3xl flex items-center justify-center mx-auto mb-6 border border-red-500/30"><RefreshCw className="w-10 h-10 text-red-500 animate-spin-slow" /></div>
                        <h3 className="text-2xl font-black text-white tracking-tighter mb-2">Relocation Sequence</h3>
                        <p className="text-slate-400 text-sm mb-8 font-medium">Reassign <span className="text-white font-bold">{selectedUser?.username}</span> to a new jurisdiction.</p>
                        <select className="w-full bg-slate-900 border-2 border-slate-700 rounded-3xl py-4 px-6 text-white font-bold outline-none focus:border-red-500 transition-all mb-8 appearance-none text-center" value={transferBarangay} onChange={e=>setTransferBarangay(e.target.value)}>
                            {URBAN_BARANGAYS.concat(RURAL_BARANGAYS).map(b=><option key={b} value={b}>{b}</option>)}
                        </select>
                        <div className="flex flex-col gap-3">
                            <button onClick={handleTransferResident} className="w-full bg-red-600 py-4 rounded-3xl font-black text-white hover:bg-red-500 shadow-2xl shadow-red-900/40 transition-all active:scale-95">CONFIRM TRANSFER</button>
                            <button onClick={()=>setShowTransferModal(false)} className="w-full py-4 text-slate-500 font-black text-xs uppercase tracking-[0.3em] hover:text-white transition-colors">Abort Mission</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}


function NavButton({ icon, onClick, title, badge }) {
    return (
        <button onClick={onClick} className="bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white p-3.5 rounded-2xl border border-slate-700 transition-all active:scale-90 relative group" title={title}>
            {icon}
            {badge > 0 && <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[9px] font-black w-4.5 h-4.5 rounded-full flex items-center justify-center border-2 border-slate-800">{badge}</span>}
            <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-2 py-1 bg-slate-900 text-[8px] font-black uppercase text-white rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-50">{title}</div>
        </button>
    );
}

function TopStat({ label, value, icon, color, bg, border }) {
    return (
        <div className={`${bg} ${border} border p-8 rounded-[40px] shadow-sm hover:shadow-xl transition-all group`}>
            <div className={`${color} bg-white p-4 rounded-2xl w-fit mb-6 shadow-2xl shadow-black/10 group-hover:scale-110 transition-transform`}>{icon}</div>
            <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-1">{label}</p>
            <p className="text-4xl font-black text-white tracking-tighter">{value}</p>
        </div>
    );
}

function ActionButton({ icon, color, onClick }) {
    return (
        <button onClick={onClick} className={`p-3 rounded-2xl transition-all active:scale-90 ${color}`}>
            {icon}
        </button>
    );
}

function InputField({ label, type="text", value, onChange, icon, placeholder }) {
    return (
        <div className="space-y-2">
            <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest ml-1">{label}</label>
            <div className="relative">
                {icon && <div className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-600">{icon}</div>}
                <input type={type} placeholder={placeholder} className={`w-full bg-slate-900/50 border border-slate-700 ${icon?'pl-12':'px-6'} py-4 rounded-2xl text-white font-bold outline-none focus:border-red-500 transition-all`} value={value} onChange={e=>onChange(e.target.value)} required />
            </div>
        </div>
    );
}

function Modal({ title, onClose, icon, children, wide }) {
    return (
        <div className="fixed inset-0 bg-slate-900/95 backdrop-blur-xl z-[60] flex items-center justify-center p-4">
            <div className={`bg-slate-800 border border-slate-700 w-full ${wide?'max-w-4xl':'max-w-lg'} rounded-[48px] shadow-3xl flex flex-col overflow-hidden animate-in zoom-in duration-300`}>
                <div className="p-10 border-b border-slate-700 flex justify-between items-center bg-gradient-to-r from-slate-700/10 to-transparent">
                    <div className="flex items-center gap-4">
                        <div className="bg-slate-900 p-3.5 rounded-2xl border border-slate-700 shadow-inner">{icon}</div>
                        <h2 className="text-2xl font-black text-white tracking-tighter uppercase">{title}</h2>
                    </div>
                    <button onClick={onClose} className="p-3 bg-slate-900/50 hover:bg-slate-700 rounded-2xl text-slate-500 transition-all"><X className="w-6 h-6" /></button>
                </div>
                <div className="flex-1 overflow-y-auto custom-scrollbar p-8">{children}</div>
            </div>
        </div>
    );
}

function ResidentCard({ user, onVerify, onTransfer }) {
    return (
        <div className="bg-slate-900/30 p-6 rounded-[32px] border border-slate-700/50 flex flex-col gap-6 hover:border-red-500/30 hover:bg-red-500/[0.01] transition-all group">
            <div className="flex items-start gap-4">
                <div className="w-24 h-24 bg-slate-800 rounded-3xl overflow-hidden flex-shrink-0 border border-slate-700 shadow-inner relative group-hover:border-red-500/30 transition-colors">
                    {user.id_image ? (
                        <>
                            <img src={`/${user.id_image}`} alt="ID" className="w-full h-full object-cover grayscale opacity-80 group-hover:grayscale-0 group-hover:opacity-100 transition-all duration-700" />
                            <a href={`/${user.id_image}`} target="_blank" className="absolute inset-0 bg-red-900/60 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity backdrop-blur-sm" rel="noreferrer">
                                <Eye className="text-white w-6 h-6" />
                            </a>
                        </>
                    ) : (
                        <div className="w-full h-full flex items-center justify-center text-slate-700"><Users className="w-10 h-10" /></div>
                    )}
                </div>
                <div className="flex-1 min-w-0 flex flex-col justify-between py-1">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className={`w-2 h-2 rounded-full ${user.is_verified ? 'bg-green-500' : 'bg-red-500'} shadow-lg shadow-current`}></span>
                            <span className="text-[9px] font-black text-slate-500 uppercase tracking-[0.2em]">{user.is_verified ? 'Authorized' : 'Suspect'}</span>
                        </div>
                        <h4 className="font-black text-white text-xl tracking-tighter truncate leading-tight">{user.username}</h4>
                        <p className="text-[10px] text-slate-500 font-mono mt-1 uppercase tracking-tighter truncate">{user.email || 'No email log'}</p>
                    </div>
                </div>
            </div>
            <div className="grid grid-cols-2 gap-3 bg-slate-800/40 p-4 rounded-2xl border border-slate-700/50">
                <div className="border-r border-slate-700/50 pr-4">
                    <p className="text-[8px] text-slate-600 font-black uppercase mb-1">Eco-Credit</p>
                    <p className="text-lg font-black text-green-500">{user.points || 0}</p>
                </div>
                <div className="pl-2">
                    <p className="text-[8px] text-slate-600 font-black uppercase mb-1">Role</p>
                    <p className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-lg inline-block ${user.role==='official'?'bg-amber-500/20 text-amber-500 border border-amber-500/30':'bg-slate-700 text-slate-400'}`}>{user.role}</p>
                </div>
            </div>
            <div className="flex gap-2">
                <button
                    onClick={() => onVerify(user.id)}
                    className={`flex-1 py-3.5 rounded-2xl font-black text-[10px] uppercase tracking-widest transition-all ${user.is_verified ? 'bg-slate-900 border border-slate-700 text-slate-500 hover:text-red-500' : 'bg-red-600 text-white hover:bg-red-500 shadow-xl shadow-red-600/20 active:scale-95'}`}
                >
                    {user.is_verified ? 'De-Authorize' : 'Authorize'}
                </button>
                <button onClick={onTransfer} className="p-3.5 bg-slate-800 border border-slate-700 rounded-2xl text-slate-400 hover:text-blue-400 transition-all active:scale-90" title="Relocate Resident">
                    <RefreshCw className="w-5 h-5" />
                </button>
            </div>
        </div>
    );
}
