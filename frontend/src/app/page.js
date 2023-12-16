import Image from "next/image";
import Button from "../components/Button";

export default function Home() {
  return (
    <main className="quadro">
      <div className="coluna">
        <h1 className="categoria">Ciência</h1>
        <Button amount={200} link="question?amount=200"></Button>
        <Button amount={400} link=""></Button>
        <Button amount={600} link=""></Button>
        <Button amount={800} link=""></Button>
        <Button amount={1000} link=""></Button>
      </div>
      <div className="coluna">
        <h1 className="categoria">Cultura</h1>
        <Button amount={200} link=""></Button>
        <Button amount={400} link=""></Button>
        <Button amount={600} link=""></Button>
        <Button amount={800} link=""></Button>
        <Button amount={1000} link=""></Button>
      </div>
      <div className="coluna">
        <h1 className="categoria">Desporto</h1>
        <Button amount={200} link=""></Button>
        <Button amount={400} link=""></Button>
        <Button amount={600} link=""></Button>
        <Button amount={800} link=""></Button>
        <Button amount={1000} link=""></Button>
      </div>
      <div className="coluna">
        <h1 className="categoria">Entretenimento</h1>
        <Button amount={200} link=""></Button>
        <Button amount={400} link=""></Button>
        <Button amount={600} link=""></Button>
        <Button amount={800} link=""></Button>
        <Button amount={1000} link=""></Button>
      </div>
      <div className="coluna">
        <h1 className="categoria">Geografia</h1>
        <Button amount={200} link=""></Button>
        <Button amount={400} link=""></Button>
        <Button amount={600} link=""></Button>
        <Button amount={800} link=""></Button>
        <Button amount={1000} link=""></Button>
      </div>
    </main>
  );
}
