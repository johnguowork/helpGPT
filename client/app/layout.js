import '@styles/globals.css'
import { Inter } from 'next/font/google'
import 'bootstrap/dist/css/bootstrap.css';
import "react-toastify/dist/ReactToastify.css";



const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'HelpGPT',
  description: 'HelpGPT',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
    
      <body className={inter.className}>{children}</body>
      
    </html>
  )
}
