import os

path = 'frontend/src/pages/Dashboard.jsx'

def fix():
    if not os.path.exists(path):
        print("File not found")
        return

    # Read the file with a robust encoding
    try:
        with open(path, 'rb') as f:
            raw_data = f.read()
        content = raw_data.decode('cp1252', errors='ignore')
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # We want to find the end of the original sub-components.
    # The original file ended with functional sub-components like SidebarItem, StatCard, EventItem, etc.
    # The last one was likely FileCheck.
    
    marker = 'function FileCheck'
    index = content.rfind(marker) # Find the last occurrence
    
    if index == -1:
        print("Could not find FileCheck marker")
        # Try finding another common sub-component
        marker = 'function SidebarItem'
        index = content.rfind(marker)
        if index == -1:
            print("Could not find any stable markers")
            return

    # Find the end of this component (the matching closing brace)
    # We'll look for the first '}' after the marker and then see if there are more shortly after.
    # A better way is to find the LAST closing brace before any corrupted code.
    
    # Let's just find the last stable '}' before the first occurrence of corrupted characters or my 'ProfileModal' appends.
    # I'll look for where I first tried to append ProfileModal.
    
    split_marker = 'function ProfileModal'
    first_append = content.find(split_marker)
    
    if first_append != -1:
        healthy_part = content[:first_append].strip()
        # Ensure it ends with a closing brace
        last_brace = healthy_part.rfind('}')
        if last_brace != -1:
            healthy_part = healthy_part[:last_brace+1]
    else:
        healthy_part = content.strip()

    # Define the correct ProfileModal component
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

    with open(path, 'w', encoding='utf-8') as f:
        f.write(healthy_part)
        f.write(profile_modal_code)
    
    print("Dashboard.jsx repaired successfully")

if __name__ == "__main__":
    fix()
