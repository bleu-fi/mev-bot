"use client";

import { normalize } from "viem/ens";
import { Footer } from "#/components/Footer";
import { Header } from "#/components/Header";
import { Loading } from "#/components/Loading";
import { FreeMevReceipt, MevReceipt } from "#/components/Receipts";
import { publicClient } from "#/utils/publicClient";
import { scanAddressMEV, IAddressMevData } from "#/utils/zeroMevApi";
import { useEffect, useState } from "react";
import { Address } from "viem";

export default function Page({
  params,
}: {
  params: {
    address: string;
  };
}) {
  const [mevData, setMevData] = useState<IAddressMevData | undefined>();
  const [loading, setLoading] = useState(true);

  async function loadData() {
    if (params.address) {
      const addressToCheck = params.address.includes(".eth")
        ? await (publicClient.getEnsAddress({
            name: normalize(params.address),
          }) as Promise<Address>)
        : params.address;
      const newMevData = await scanAddressMEV(addressToCheck as Address);
      setMevData(newMevData);
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, [params.address]);

  if (loading) {
    return (
      <div className="flex w-full justify-center h-full">
        <div className="flex flex-col items-center gap-8 justify-between w-full md:w-1/2">
          <Header address={params.address} />
          <Loading />
          <Footer />
        </div>
      </div>
    );
  }

  return (
    <div className="flex w-full justify-center h-full">
      {mevData && mevData?.totalAmountUsd ? (
        <MevReceipt mevData={mevData} address={params.address} />
      ) : (
        <FreeMevReceipt address={params.address} />
      )}
    </div>
  );
}
