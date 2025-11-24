import { useEffect, useState } from 'react';
import './App.css'
import { Input } from './components/ui/input';
import { Button } from './components/ui/button';

function App() {
  const [msg, setMsg] = useState<string>("");
  const [user1, setUser1] = useState<string>("");
  const [user2, setUser2] = useState<string>("");

  // const getMsg = async () => {
  //   const response = await fetch('http://localhost:8000/');
  //   const data = await response.json();
  //   setMsg(data.message);
  // }

  // useEffect(() => {
  //   getMsg();
  // }, []);

  return (
    <>
      <header className="flex flex-col items-center gap-2">
        <h1 className="font-bold text-6xl text-gray-700">Letterboxd Neighbour</h1>
        <p className="text-xl">Measure film taste between two Letterboxd users.</p>
      </header>

      <section className="mt-6 gap-2 flex flex-col items-center w-full">
        <Input placeholder="Username 1" className="w-1/2" onChange={
          (e) => setUser1(e.target.value)
        }/>
        <Input placeholder="Username 2" className="w-1/2" onChange={
          (e) => setUser2(e.target.value)
        }/>
        <Button className="w-1/2 bg-gray-700 text-white hover:cursor-pointer hover:bg-gray-700/90">Find Neighbour Films</Button>
      </section>
    </>
  )
}

export default App
