import os

path = 'frontend/src/pages/Dashboard.jsx'

# Correct ProfileModal component definition
profile_modal_code = """
function ProfileModal({ formData, setFormData, onClose, onSubmit, loading }) {
    return (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in duration-300">
            <div className="bg-white rounded-5xl w-full max-w-lg overflow-hidden shadow-2xl">
                <div className="p-8 pb-4 flex justify-between items-center border-b border-slate-50">
                    <div>
                        <h2 className="text-2xl font-black text-slate-800 tracking-tighter">My Account</h2>
                        <p className="text-sm font-medium text-slate-400">Manage your personal information</p>
                    </div>
                    <button onClick={onClose} className="p-3 bg-slate-50 hover:bg-slate-100 rounded-2xl text-slate-400 transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <form onSubmit={onSubmit} className="p-8 space-y-5">
                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Username</label>
                        <div className="relative">
                            <User className="w-5 h-5 text-slate-300 absolute left-4 top-4" />
                            <input
                                type="text"
                                value={formData.username}
                                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                className="w-full bg-slate-50 pl-12 pr-6 py-4 rounded-2xl border border-slate-100 focus:border-green-500 focus:ring-4 focus:ring-green-50 outline-none transition-all font-bold text-slate-800"
                                required
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Email Address</label>
                        <div className="relative">
                            <Mail className="w-5 h-5 text-slate-300 absolute left-4 top-4" />
                            <input
                                type="email"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                className="w-full bg-slate-50 pl-12 pr-6 py-4 rounded-2xl border border-slate-100 focus:border-green-500 focus:ring-4 focus:ring-green-50 outline-none transition-all font-bold text-slate-800"
                                required
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Phone Number</label>
                        <div className="relative">
                            <Phone className="w-5 h-5 text-slate-300 absolute left-4 top-4" />
                            <input
                                type="text"
                                value={formData.phone_number}
                                onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                                className="w-full bg-slate-50 pl-12 pr-6 py-4 rounded-2xl border border-slate-100 focus:border-green-500 focus:ring-4 focus:ring-green-50 outline-none transition-all font-bold text-slate-800"
                                required
                            />
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">New Password (leave blank to keep current)</label>
                        <div className="relative">
                            <Lock className="w-5 h-5 text-slate-300 absolute left-4 top-4" />
                            <input
                                type="password"
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                placeholder="••••••••"
                                className="w-full bg-slate-50 pl-12 pr-6 py-4 rounded-2xl border border-slate-100 focus:border-green-500 focus:ring-4 focus:ring-green-50 outline-none transition-all font-bold text-slate-800"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-slate-900 text-white font-extrabold py-5 rounded-3xl hover:bg-slate-800 active:scale-95 transition-all text-lg shadow-xl shadow-slate-100 disabled:opacity-50 mt-4"
                    >
                        {loading ? 'Saving Changes...' : 'Update Profile'}
                    </button>
                </form>
            </div>
        </div>
    );
}
"""

if os.path.exists(path):
    with open(path, 'r', encoding='cp1252', errors='ignore') as f:
        lines = f.readlines()
    
    # Keep lines up to 880 (original end of Dashboard.jsx)
    # The corrupted part starts around line 881
    # We want to keep everything up to the last valid closing brace of Dashboard component and sub-components.
    
    # Finding the second to last '}' might be risky. 
    # Let's find 'function FileCheck' which is at the very end of the original file.
    file_check_index = -1
    for i, line in enumerate(lines):
        if 'function FileCheck' in line:
            file_check_index = i
            break
            
    if file_check_index != -1:
        # Find the end of FileCheck (usually about 20 lines later)
        end_index = -1
        for j in range(file_check_index, len(lines)):
            if lines[j].strip() == '}':
                end_index = j
                # Keep looking for any further closing braces that might belong to the original file
                # But actually FileCheck was the last one.
        
        if end_index != -1:
            clean_lines = lines[:end_index+1]
            # Append the new Modal
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(clean_lines)
                f.write("\n" + profile_modal_code + "\n")
            print("Successfully fixed Dashboard.jsx")
        else:
            print("Could not find end of FileCheck")
    else:
        print("Could not find FileCheck component")
else:
    print("File not found")
