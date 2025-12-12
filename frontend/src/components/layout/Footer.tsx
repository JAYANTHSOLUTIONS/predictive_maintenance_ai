export function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 px-6 py-3">
      <div className="flex items-center justify-between text-xs text-slate-600">
        <div>
          <span>© 2025 OEM Aftersales Intelligence Platform. All rights reserved.</span>
        </div>
        <div className="flex items-center space-x-4">
          <a href="#" className="hover:text-slate-900">
            Terms of Service
          </a>
          <span>•</span>
          <a href="#" className="hover:text-slate-900">
            Privacy Policy
          </a>
          <span>•</span>
          <a href="#" className="hover:text-slate-900">
            Documentation
          </a>
        </div>
      </div>
    </footer>
  );
}
