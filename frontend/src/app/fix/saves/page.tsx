"use client";

import { useState, useEffect } from "react";
import * as api from "../../../lib/api";


export default function Saves()  {
  const [save, setSave] = useState<string>();
  const [options, setOptions] = useState<string[]>([]);
  const [submitTrigger, setSubmitTrigger] = useState<boolean>(false);

  useEffect(() => {
    const fetchData = async () => {
      const data = await api.fixListSaves();
      setOptions(data);
    };

    fetchData();
  }, [submitTrigger]);

  const submit = () => {
    api.fixSaves(save);
    setSubmitTrigger(!submitTrigger);
  };

  const updateSave = (s: string) => {
    setSave(s);
  };

  return (
    <div className="flex h-screen w-screen items-center justify-center text-white">
      <div className="block">
        <h1 className="text-center uppercase text-5xl font-bold mb-8">
          Update Save
        </h1>
        <select 
          className="py-4 w-full m-auto mt-8 bg-yellow-700 uppercase text-xl"
          onChange={(e) => updateSave(e.target.value)}>
            {options.map((option, index) => (
              <option key={index} value={option}>
                {option}
              </option>
            ))}
        </select>
        <button
          className="py-4 w-full m-auto mt-8 bg-green-700 uppercase text-xl"
          onClick={(_) => submit()}
        >
          Submit
        </button>
      </div>
    </div>
  );
}