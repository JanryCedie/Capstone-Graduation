import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Leaf, Lock, User } from 'lucide-react';
import { URBAN_BARANGAYS, RURAL_BARANGAYS } from '../data/barangays';

export default function Login() {
    const [formData, setFormData] = useState({ username: '', password: '', barangay: URBAN_BARANGAYS[0] });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        // Resident Login Access Control
        const devResident = {
            id: 100,
            username: 'Dev_Resident',
            role: 'resident',
            barangay: formData.barangay || 'Santa Monica',
            points: 150,
            total_earned: 150,
            is_verified: true
        };
        localStorage.setItem('user', JSON.stringify(devResident));
        localStorage.setItem('token', 'DEV_BYPASS_TOKEN');
        
        navigate('/dashboard');
    };

    return (
        <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
            <div className="bg-white p-8 rounded-3xl shadow-xl max-w-sm w-full">
                <div className="flex justify-center mb-6">
                    <div className="bg-green-100 p-3 rounded-full">
                        <Leaf className="w-8 h-8 text-green-600" />
                    </div>
                </div>
                <h2 className="text-2xl font-bold text-center text-slate-800 mb-1">Welcome Back</h2>
                <p className="text-center text-slate-500 text-sm mb-6">Log in to your Eco Warrior portal</p>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {error && (
                        <div className="bg-red-50 text-red-600 text-xs p-3 rounded-xl border border-red-100 text-center">
                            {error}
                        </div>
                    )}

                    <div>
                        <label className="block text-xs font-bold text-slate-400 uppercase mb-1 ml-1">Username</label>
                        <div className="relative">
                            <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                            <input
                                type="text"
                                className="w-full pl-9 pr-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                                placeholder="Enter username (auto bypass)"
                                value={formData.username}
                                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-slate-400 uppercase mb-1 ml-1">Your Barangay</label>
                        <select
                            className="w-full px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                            value={formData.barangay}
                            onChange={(e) => setFormData({ ...formData, barangay: e.target.value })}
                        >
                            <optgroup label="Urban Barangays">
                                {URBAN_BARANGAYS.map(b => <option key={b} value={b}>{b}</option>)}
                            </optgroup>
                            <optgroup label="Rural Barangays">
                                {RURAL_BARANGAYS.map(b => <option key={b} value={b}>{b}</option>)}
                            </optgroup>
                        </select>
                    </div>

                    <div>
                        <label className="block text-xs font-bold text-slate-400 uppercase mb-1 ml-1">Password</label>
                        <div className="relative">
                            <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                            <input
                                type="password"
                                className="w-full pl-9 pr-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                                placeholder="•••••••• (auto bypass)"
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            />
                        </div>
                        <div className="flex justify-end mt-1">
                            <Link to="/forgot-password" className="text-xs font-medium text-green-600 hover:text-green-700">
                                Forgot Password?
                            </Link>
                        </div>
                    </div>

                    <button
                        disabled={loading}
                        type="submit"
                        className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-xl transition-all shadow-lg active:scale-95 disabled:opacity-50 mt-2"
                    >
                        {loading ? 'Logging in...' : 'Sign In'}
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-slate-600">
                    Don't have an account?{' '}
                    <Link to="/signup" className="text-green-600 hover:text-green-700 font-medium">
                        Sign up
                    </Link>
                </p>
            </div>
        </div>
    );
}
