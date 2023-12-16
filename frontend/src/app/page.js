import Image from "next/image";
import Button from "src/app/components";

export default function Home() {
  return (
    <main className="quadro">
      <div className="coluna">
        <h1 className="categoria">Ciência</h1>
        <Button>200</Button>
        <Button>400</Button>
        <Button>600</Button>
        <Button>800</Button>
        <Button>1000</Button>
      </div>
      <div className="coluna">
        <h1 className="categoria">Cultura</h1>
        <Button>200</Button>
        <Button>400</Button>
        <Button>600</Button>
        <Button>800</Button>
        <Button>1000</Button>
      </div>
      <div className="coluna">
        <h1 className="categoria">Desporto</h1>
        <Button>200</Button>
        <Button>400</Button>
        <Button>600</Button>
        <Button>800</Button>
        <Button>1000</Button>
      </div>
      <div className="coluna">
        <h1 className="categoria">Entretenimento</h1>
        <Button>200</Button>
        <Button>400</Button>
        <Button>600</Button>
        <Button>800</Button>
        <Button>1000</Button>
      </div>
      <div className="coluna">
        <h1 className="categoria">Geografia</h1>
        <Button>200</Button>
        <Button>400</Button>
        <Button>600</Button>
        <Button>800</Button>
        <Button>1000</Button>
      </div>
    </main>
  );
}
