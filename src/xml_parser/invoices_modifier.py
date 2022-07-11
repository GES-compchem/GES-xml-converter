from io import BytesIO, TextIOWrapper
from typing import Dict, Tuple
from pandas import DataFrame

DEFAULT_LOOKUP_TABLE = {
    "DatiTrasmissione|IdTrasmittente|IdPaese" : "Tras_Paese",
    "DatiTrasmissione|IdTrasmittente|IdCodice" : "Tras_ID",
    "DatiTrasmissione|ProgressivoInvio" : "Tras_prog",
    "DatiTrasmissione|FormatoTrasmissione" : "Tras_form",
    "DatiTrasmissione|CodiceDestinatario" : "Tras_dest",
    "CedentePrestatore|DatiAnagrafici|IdFiscaleIVA|IdPaese" : "Forn_Paese",
    "CedentePrestatore|DatiAnagrafici|IdFiscaleIVA|IdCodice" : "Forn_IVA",
    "CedentePrestatore|DatiAnagrafici|CodiceFiscale" : "Forn_CF",
    "CedentePrestatore|DatiAnagrafici|Anagrafica|Denominazione" : "Forn_Nome",
    "CedentePrestatore|DatiAnagrafici|Anagrafica|CodEORI" : "Forn_CodEORI",
    "CedentePrestatore|DatiAnagrafici|RegimeFiscale" : "Forn_Reg",
    "CedentePrestatore|Sede|Indirizzo" : "Forn_Indirizzo",
    "CedentePrestatore|Sede|CAP" : "Fonr_CAP",
    "CedentePrestatore|Sede|Comune" : "Forn_Comune",
    "CedentePrestatore|Sede|Nazione" : "Forn_Paese_ced",
    "CedentePrestatore|IscrizioneREA|Ufficio" : "Forn_Provincia",
    "CedentePrestatore|IscrizioneREA|NumeroREA" : "Forn_REA",
    "CedentePrestatore|IscrizioneREA|CapitaleSociale" : "Forn_CS",
    "CedentePrestatore|IscrizioneREA|SocioUnico" : "Forn_SU",
    "CedentePrestatore|IscrizioneREA|StatoLiquidazione" : "Forn_SL",
    "CedentePrestatore|Contatti|Telefono" : "Forn_tel",
    "CessionarioCommittente|DatiAnagrafici|IdFiscaleIVA|IdPaese" : "Soc_Paese_an",
    "CessionarioCommittente|DatiAnagrafici|IdFiscaleIVA|IdCodice" : "Soc_IVA",
    "CessionarioCommittente|DatiAnagrafici|Anagrafica|Denominazione" : "Soc_Nome",
    "CessionarioCommittente|Sede|Indirizzo" : "Soc_Indirizzo",
    "CessionarioCommittente|Sede|CAP" : "Soc_CAP",
    "CessionarioCommittente|Sede|Comune" : "Soc_Comune",
    "CessionarioCommittente|Sede|Nazione" : "Soc_Paese",
    "DatiGenerali|DatiGeneraliDocumento|TipoDocumento" : "Ft_tipo",
    "DatiGenerali|DatiGeneraliDocumento|Divisa" : "Ft_currency",
    "DatiGenerali|DatiGeneraliDocumento|Data" : "Ft_dt",
    "DatiGenerali|DatiGeneraliDocumento|Numero" : "Ft_num",
    "DatiGenerali|DatiGeneraliDocumento|ImportoTotaleDocumento" : "Ft_totale_doc",
    "DatiGenerali|DatiGeneraliDocumento|Causale" : "Ft_causale",
    "DatiBeniServizi|DettaglioLinee|NumeroLinea" : "Ft_linee",
    "DatiBeniServizi|DettaglioLinee|Descrizione" : "Ft_linee_descr",
    "DatiBeniServizi|DettaglioLinee|PrezzoUnitario" : "Ft_linee_prezzo_uni",
    "DatiBeniServizi|DettaglioLinee|PrezzoTotale" : "Ft_linee_prezzo_tot",
    "DatiBeniServizi|DettaglioLinee|AliquotaIVA" : "Ft_linee_IVAal",
    "DatiBeniServizi|DettaglioLinee|Natura" : "Ft_linee_nat",
    "DatiBeniServizi|DatiRiepilogo|AliquotaIVA" : "Ft_riep_IVAal",
    "DatiBeniServizi|DatiRiepilogo|Natura" : "Ft_riep_nat",
    "DatiBeniServizi|DatiRiepilogo|ImponibileImporto" : "Ft_riep_imponibile",
    "DatiBeniServizi|DatiRiepilogo|Imposta" : "Ft_riep_imposta",
    "DatiBeniServizi|DatiRiepilogo|RiferimentoNormativo" : "Ft_riep_law",
    "DatiPagamento|CondizioniPagamento" : "Ft_cond_pag",
    "DatiPagamento|DettaglioPagamento|ModalitaPagamento" : "Ft_mod_pag",
    "DatiPagamento|DettaglioPagamento|DataScadenzaPagamento" : "Ft_dt_scad",
    "DatiPagamento|DettaglioPagamento|ImportoPagamento" : "Ft_imp_pag",
    "DatiPagamento|DettaglioPagamento|IBAN" : "Ft_IBAN",
    "DatiTrasmissione|ContattiTrasmittente|Telefono" : "Ft_tel",
    "DatiTrasmissione|ContattiTrasmittente|Email" : "Ft_mail",
    "DatiTrasmissione|PECDestinatario" : "Ft_pec",
    "CedentePrestatore|Sede|Provincia" : "Ft_Forn_prov",
    "CessionarioCommittente|Sede|Provincia" : "Ft_prov_Soc",
    "DatiGenerali|DatiOrdineAcquisto|RiferimentoNumeroLinea" : "Ft_linea_law",
    "DatiGenerali|DatiOrdineAcquisto|IdDocumento" : "Ft_linea_ord",
    "DatiGenerali|DatiDDT|NumeroDDT" : "Ft_linea_DDT",
    "DatiGenerali|DatiDDT|DataDDT" : "Ft_linea_dt_DDT",
    "DatiGenerali|DatiDDT|RiferimentoNumeroLinea" : "Ft_linea_rif",
    "DatiGenerali|DatiTrasporto|IndirizzoResa|Indirizzo" : "Trasp_indirizzo",
    "DatiGenerali|DatiTrasporto|IndirizzoResa|CAP" : "Trasp_CAP",
    "DatiGenerali|DatiTrasporto|IndirizzoResa|Comune" : "Trasp_Comune",
    "DatiGenerali|DatiTrasporto|IndirizzoResa|Provincia" : "Trasp_Prov",
    "DatiGenerali|DatiTrasporto|IndirizzoResa|Nazione" : "Trasp_Paese",
    "DatiBeniServizi|DettaglioLinee|CodiceArticolo|CodiceTipo" : "Art_tipo",
    "DatiBeniServizi|DettaglioLinee|CodiceArticolo|CodiceValore" : "Art_cod_val",
    "DatiBeniServizi|DettaglioLinee|Quantita" : "Art_qt",
    "DatiBeniServizi|DettaglioLinee|UnitaMisura" : "Art_UM",
    "DatiBeniServizi|DettaglioLinee|AltriDatiGestionali|TipoDato" : "Ft_linee_tipo",
    "DatiBeniServizi|DettaglioLinee|AltriDatiGestionali|RiferimentoTesto" : "Ft_linee_rif",
    "DatiBeniServizi|DettaglioLinee|TipoCessionePrestazione" : "Ft_linee_cess",
    "DatiBeniServizi|DatiRiepilogo|EsigibilitaIVA" : "Ft_riep_esig_IVA",
    "DatiPagamento|DettaglioPagamento|DataRiferimentoTerminiPagamento" : "Ft_pag_dt_rif",
    "DatiPagamento|DettaglioPagamento|GiorniTerminiPagamento" : "Ft_pag_gg",
    "DatiPagamento|DettaglioPagamento|IstitutoFinanziario" : "Ft_pag_bank",
    "DatiPagamento|DettaglioPagamento|BIC" : "Ft_pag_BIC",
    "DatiPagamento|DettaglioPagamento|CodicePagamento" : "Ft_pag_cod",
    "Allegati|NomeAttachment" : "Ft_allegato_nome",
    "Allegati|FormatoAttachment" : "Ft_all_format",
    "Allegati|Attachment" : "Ft_allegato",
    "CedentePrestatore|Sede|NumeroCivico" : "Forn_civico",
    "CedentePrestatore|Contatti" : "Forn_contatti",
    "CessionarioCommittente|DatiAnagrafici|CodiceFiscale" : "Soc_CF2",
    "DatiGenerali|DatiContratto|IdDocumento" : "Gen_Iddoc",
    "TerzoIntermediarioOSoggettoEmittente|DatiAnagrafici|IdFiscaleIVA|IdPaese" : "Int_Paese",
    "TerzoIntermediarioOSoggettoEmittente|DatiAnagrafici|IdFiscaleIVA|IdCodice" : "Int_cod",
    "TerzoIntermediarioOSoggettoEmittente|DatiAnagrafici|Anagrafica|Denominazione" : "Int_nome",
    "DatiGenerali|DatiOrdineAcquisto|Data" : "Ordine_dt",
    "DatiGenerali|DatiRicezione|IdDocumento" : "Gen_doc_ric",
    "DatiGenerali|DatiTrasporto|DataOraConsegna" : "Gen_consegna",
    "DatiBeniServizi|DettaglioLinee|ScontoMaggiorazione|Tipo" : "Ft_linee_tipo_sc",
    "DatiBeniServizi|DettaglioLinee|ScontoMaggiorazione|Percentuale" : "Ft_linee_sconto_perc",
    "DatiBeniServizi|DettaglioLinee|ScontoMaggiorazione|Importo" : "Ft_linee_sconto_imp",
    "DatiTrasmissione|ContattiTrasmittente" : "Dati_trasmiss",
    "DatiGenerali|DatiGeneraliDocumento|DatiCassaPrevidenziale|TipoCassa" : "Prev_tipo",
    "DatiGenerali|DatiGeneraliDocumento|DatiCassaPrevidenziale|AlCassa" : "Prev_al",
    "DatiGenerali|DatiGeneraliDocumento|DatiCassaPrevidenziale|ImportoContributoCassa" : "Prev_importo",
    "DatiGenerali|DatiGeneraliDocumento|DatiCassaPrevidenziale|ImponibileCassa" : "Prev_impo",
    "DatiGenerali|DatiGeneraliDocumento|DatiCassaPrevidenziale|AliquotaIVA" : "Prev_IVAal",
    "Allegati|DescrizioneAttachment" : "All_descr",
    "CedentePrestatore|DatiAnagrafici|Anagrafica|Titolo" : "Ced_titolo",
    "CedentePrestatore|Contatti|Fax" : "Ced_fax",
    "CedentePrestatore|Contatti|Email" : "Ced_mail",
    "TerzoIntermediarioOSoggettoEmittente|DatiAnagrafici|CodiceFiscale" : "Int_CF",
    "SoggettoEmittente" : "Sogg_em",
    "DatiPagamento|DettaglioPagamento|Beneficiario" : "Pg_benef",
    "DatiBeniServizi|DatiRiepilogo|Arrotondamento" : "tec1",
    "CessionarioCommittente|Sede|NumeroCivico" : "tec2",
    "DatiGenerali|DatiGeneraliDocumento|Arrotondamento" : "tec3",
    "DatiGenerali|DatiGeneraliDocumento|DatiBollo|BolloVirtuale" : "BolloVirtuale",
    "DatiGenerali|DatiGeneraliDocumento|DatiBollo|ImportoBollo" : "Bollo_imp",
    "DatiPagamento|DettaglioPagamento|ABI" : "ABI",
    "DatiPagamento|DettaglioPagamento|CAB" : "CAB",
    "DatiGenerali|DatiOrdineAcquisto|CodiceCUP" : "CUP",
    "DatiBeniServizi|DettaglioLinee|DataInizioPeriodo" : "Ft_linee_DT_inizio",
    "DatiBeniServizi|DettaglioLinee|DataFinePeriodo" : "Ft_linee_DT_fine",
    "CedentePrestatore|RiferimentoAmministrazione" : "tec4",
    "DatiBeniServizi|DettaglioLinee|AltriDatiGestionali|RiferimentoData" : "Ft_linee_dt_rif",
    "DatiBeniServizi|DettaglioLinee|AltriDatiGestionali|RiferimentoNumero" : "Ft_linee_num_rif",
    "DatiGenerali|DatiGeneraliDocumento|DatiRitenuta|TipoRitenuta" : "Rit",
    "DatiGenerali|DatiGeneraliDocumento|DatiRitenuta|ImportoRitenuta" : "Rit_imp",
    "DatiGenerali|DatiGeneraliDocumento|DatiRitenuta|AliquotaRitenuta" : "Rit_al",
    "DatiGenerali|DatiGeneraliDocumento|DatiRitenuta|CausalePagamento" : "Rit_causale",
    "DatiBeniServizi|DettaglioLinee|Ritenuta" : "Rit_linee_dett",
    "DatiGenerali|DatiOrdineAcquisto|CodiceCommessaConvenzione" : "Ft_comm",
    "DatiGenerali|DatiContratto|Data" : "Contr_dt",
    "DatiGenerali|DatiContratto|CodiceCUP" : "Contr_CUP",
    "DatiGenerali|DatiFattureCollegate|RiferimentoNumeroLinea" : "Ftcoll_linea",
    "DatiGenerali|DatiFattureCollegate|IdDocumento" : "Ftcoll_ID",
    "DatiGenerali|DatiFattureCollegate|Data" : "Ftcoll_Dt",
    "DatiGenerali|DatiFattureCollegate|NumItem" : "Ftcoll_item",
    "DatiBeniServizi|DatiRiepilogo|SpeseAccessorie" : "SpeseAccessorie",
    "DatiGenerali|DatiGeneraliDocumento|Art73" : "Art73",
    "DatiGenerali|DatiTrasporto" : "tec5",
    "DatiBeniServizi|DettaglioLinee|RiferimentoAmministrazione" : "tec6",
    "DatiGenerali|DatiOrdineAcquisto|NumItem" : "tec7",
    "CessionarioCommittente|DatiAnagrafici|Anagrafica|CodEORI" : "tec8",
    "DatiGenerali|DatiTrasporto|TipoResa" : "tec9",
    "DatiPagamento|DettaglioPagamento|ScontoPagamentoAnticipato" : "tec10",
    "DatiPagamento|DettaglioPagamento|PenalitaPagamentiRitardati" : "tec11",
    "CedentePrestatore|StabileOrganizzazione|Indirizzo" : "tec12",
    "CedentePrestatore|StabileOrganizzazione|CAP" : "tec13",
    "CedentePrestatore|StabileOrganizzazione|Comune" : "tec14",
    "CedentePrestatore|StabileOrganizzazione|Nazione" : "tec15",
    "DatiGenerali|DatiContratto|RiferimentoNumeroLinea" : "Contr_rif_linea",
    "DatiGenerali|FatturaPrincipale|NumeroFatturaPrincipale" : "Ft_num_princ",
    "DatiGenerali|FatturaPrincipale|DataFatturaPrincipale" : "Ft_dt_princ",
    "DatiGenerali|DatiTrasporto|MezzoTrasporto" : "MezzoTrasporto",
    "DatiGenerali|DatiTrasporto|CausaleTrasporto" : "CausaleTrasporto",
    "DatiGenerali|DatiTrasporto|NumeroColli" : "NumeroColli",
    "DatiGenerali|DatiTrasporto|Descrizione" : "Descrizione",
    "DatiGenerali|DatiTrasporto|DataOraRitiro" : "DataOraRitiro",
    "Allegati|AlgoritmoCompressione" : "tec16",
    "DatiGenerali|DatiTrasporto|UnitaMisuraPeso" : "Trasp_UM",
    "DatiGenerali|DatiTrasporto|PesoLordo" : "Trasp_peso",
    "CedentePrestatore|DatiAnagrafici|Anagrafica|Nome" : "Forn_nome_an",
    "CedentePrestatore|DatiAnagrafici|Anagrafica|Cognome" : "Forn_Cogn_an"
}   
        
        
def modify_header(df: DataFrame, filler: str = " ", lookup_table: Dict[str, str] = {}) -> Tuple[DataFrame, Dict[str, str]]:
    '''
    This function simplifies the dataframe header by substitution with a pre-defiend lookup table.

        Parameters:
        -----------
            df (DataFrame): Pandas dataframe generated by the XML_converter class
            filler (str): Element to fill the gap between node fields (default: ' ')
        
        Returns:
        --------
            df (DataFrame): Pandas dataframe with a simplified column structure
    '''
    
    header = []
    new_labels: Dict[str, str] = {}

    if lookup_table == {}:
        lookup_table = DEFAULT_LOOKUP_TABLE
    
    for signature in df.columns:

        search = "|".join([x for x in signature if x != filler])

        if search in lookup_table:
            header.append(lookup_table[search])
        else:
            new_label = "unk_{}".format(len(new_labels)+1)
            header.append(new_label)
            new_labels[search] = new_label
        
    df.columns = header         #Verify if pandas offers a more convenient header changer
    
    return df, new_labels


def get_default_lookup_table() -> BytesIO:
    '''
    This function returns a standardized BytesIO stream containing the DEFAULT_LOOKUP_TABLE
        
        Returns:
        --------
            data (BytesIO): BytesIO stream encoding the DEFAULT_LOOKUP_TABLE
    '''
    
    table = ""
    for key, label in DEFAULT_LOOKUP_TABLE.items():
        table += "{}: {}\n".format(key, label)
    
    return BytesIO(table.encode('utf-8'))


def convert_to_lookup_table(instream: BytesIO) -> Dict[str, str]:
    '''
    This function converts a standardized BytesIO stream encoding a lookup table to a valid lookup table dictionary
        
        Parameters:
        -----------
            instream (BytesIO): BytesIO stream encoding the custom lookup-table

        Returns:
        --------
            table (Dict[str, str]): Dictionary containing the custom lookup-table
    '''

    
    table = {}
    textstream = TextIOWrapper(instream)
    for line in textstream:
        sline = line.strip('\n').split(":")
        if len(sline) != 2:
            raise ValueError
        table[sline[0]] = sline[1]

    return table