"""Integrador gráfico portátil. Requer apenas Python/Tk na versão fonte.
O EXE distribuído inclui o interpretador e as dependências.
"""
from datetime import date, datetime, timezone
from pathlib import Path
import argparse
import json
import os
import sys
import tempfile
import uuid
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from calendario import domingos
from acervo import ler, adicionar, validar_novo


class Integrador(tk.Tk):
    def __init__(self, initial=None, testing=False):
        super().__init__()
        self.title("Integrador de Sermões · Igreja Esperança")
        self.geometry("1080x820")
        self.minsize(850, 690)
        self.configure(bg="#f4f5ef")
        self.testing = testing
        self.path = None
        self.data = {"sermons": []}
        self.fingerprint = None
        self.calendar_rows = []
        self.loaded_year = None
        self.dirty = False
        self._resetting = True
        app_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
        self.settings = app_dir / "integrador-config.json"
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#f4f5ef")
        style.configure("TLabel", background="#f4f5ef", foreground="#243c32", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 21, "bold"))
        style.configure("TButton", padding=(12, 8), font=("Segoe UI", 10))
        style.configure("Accent.TButton", background="#304d40", foreground="white", padding=(18, 10))
        style.map("Accent.TButton", background=[("active", "#426550")])
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10))
        header = ttk.Frame(self, padding=(24,18,24,10)); header.pack(fill="x")
        ttk.Label(header, text="Acervo de sermões", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Localizar index.html…", command=self.choose_file).pack(side="right")
        self.path_label = ttk.Label(self, text="Selecione o index.html atualizado para começar.", padding=(24,0,24,10), wraplength=1000)
        self.path_label.pack(fill="x")
        self.tabs = ttk.Notebook(self); self.tabs.pack(fill="both", expand=True, padx=24, pady=(0,12))
        self.form = ttk.Frame(self.tabs, padding=20)
        self.history = ttk.Frame(self.tabs, padding=18)
        self.cal_tab = ttk.Frame(self.tabs, padding=18)
        self.tabs.add(self.form,text="  Novo sermão  "); self.tabs.add(self.history,text="  Acervo preservado  "); self.tabs.add(self.cal_tab,text="  Calendário do ano  ")
        self.form.columnconfigure(0,weight=1);self.form.columnconfigure(1,weight=1)
        self.year = tk.StringVar(value=str(date.today().year))
        ttk.Label(self.form,text="Ano").grid(row=0,column=0,sticky="w")
        self.year_input = ttk.Spinbox(self.form,from_=2026,to=4099,textvariable=self.year,width=12,command=self.update_calendar)
        self.year_input.grid(row=1,column=0,sticky="w",pady=(4,12),ipady=5)
        self.year_input.bind("<Return>",self.update_calendar);self.year_input.bind("<FocusOut>",self.update_calendar)
        ttk.Label(self.form,text="Domingo — selecione uma data da lista").grid(row=2,column=0,columnspan=2,sticky="w")
        self.sunday = ttk.Combobox(self.form,state="readonly",font=("Segoe UI",10))
        self.sunday.grid(row=3,column=0,columnspan=2,sticky="ew",pady=(4,8),ipady=5)
        self.sunday.bind("<<ComboboxSelected>>",self.update_preview)
        self.season_label=ttk.Label(self.form,text="",wraplength=940)
        self.season_label.grid(row=4,column=0,columnspan=2,sticky="w",pady=(0,14))
        self.values = {k:tk.StringVar() for k in ("series","title","preacher","url")}
        self.inputs={}
        for key, label, row, col, span in [("series","Série",5,0,1),("preacher","Preletor",5,1,1),("title","Título do sermão",7,0,2),("url","Link original do Google Drive",9,0,2)]:
            ttk.Label(self.form,text=label).grid(row=row,column=col,columnspan=span,sticky="w",padx=(0,12) if col==0 and span==1 else 0)
            widget = ttk.Combobox(self.form,textvariable=self.values[key],font=("Segoe UI",11)) if key in ("series","preacher") else ttk.Entry(self.form,textvariable=self.values[key],font=("Segoe UI",11))
            widget.grid(row=row+1,column=col,columnspan=span,sticky="ew",pady=(4,12),ipady=5,padx=(0,12) if col==0 and span==1 else 0)
            self.inputs[key]=widget
            self.values[key].trace_add("write",self.update_preview)
        self.preview=ttk.Label(self.form,text="",wraplength=940,background="#e5ebdf",padding=16)
        self.preview.grid(row=11,column=0,columnspan=2,sticky="ew",pady=(5,14))
        actions=ttk.Frame(self.form);actions.grid(row=12,column=0,columnspan=2,sticky="ew")
        self.save_button=ttk.Button(actions,text="Salvar novo sermão",style="Accent.TButton",command=self.save,state="disabled")
        self.save_button.pack(side="right")
        ttk.Button(actions,text="Limpar formulário",command=self.clear_form).pack(side="left")
        ttk.Label(self.form,text="Uma cópia de segurança é criada a cada salvamento. O acervo anterior não é alterado.",wraplength=940).grid(row=13,column=0,columnspan=2,sticky="w",pady=(14,0))
        ttk.Label(self.history,text="Consulta dos registros existentes. Links, datas e textos são preservados sem recálculo.",wraplength=940).pack(anchor="w",pady=(0,10))
        self.tree=self.make_tree(self.history,("date","title","preacher"),("Data","Sermão","Preletor"),(100,550,190))
        self.tree.bind("<<TreeviewSelect>>",self.show_record)
        self.record_text=tk.Text(self.history,height=9,wrap="word",font=("Segoe UI",10),background="white",relief="flat",padx=12,pady=12,state="disabled")
        self.record_text.pack(fill="x",pady=(12,0))
        ttk.Label(self.cal_tab,text="Calendário calculado para o ano selecionado na aba Novo sermão.\nAs regras seguem o calendário de 2026 e as recorrências confirmadas pela igreja.",wraplength=940).pack(anchor="w",pady=(0,12))
        self.cal_tree=self.make_tree(self.cal_tab,("date","celebration","season"),("Data","Domingo / celebração","Estação"),(100,560,180))
        ttk.Label(self.cal_tab,text="Setembro: Criação; 2º domingo: aniversário. Último domingo de outubro: Reforma.\nApós Pentecostes até junho; Tempo Comum a partir de julho. Datas móveis recalculadas pela Páscoa.",wraplength=940).pack(anchor="w",pady=(12,0))
        self.status=tk.StringVar(value="O programa atualiza o arquivo local. A publicação continua pelo GitHub.")
        ttk.Label(self,textvariable=self.status,padding=(24,0,24,14),wraplength=1000).pack(fill="x")
        self.protocol("WM_DELETE_WINDOW",self.close_app)
        self.update_calendar()
        self._resetting=False;self.dirty=False
        if initial:
            self.load_file(Path(initial))
        elif not testing:
            try:
                stored=json.loads(self.settings.read_text(encoding="utf-8")).get("index")
                if stored and Path(stored).is_file(): self.load_file(Path(stored))
            except (OSError,ValueError): pass
            if self.path is None: self.after(150,self.choose_file)

    def make_tree(self,parent,columns,labels,widths):
        frame=ttk.Frame(parent);frame.pack(fill="both",expand=True)
        tree=ttk.Treeview(frame,columns=columns,show="headings",selectmode="browse")
        scroll=ttk.Scrollbar(frame,orient="vertical",command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        for c,label,width in zip(columns,labels,widths):tree.heading(c,text=label);tree.column(c,width=width,minwidth=80)
        scroll.pack(side="right",fill="y");tree.pack(fill="both",expand=True)
        return tree

    def choose_file(self):
        if self.dirty and not messagebox.askyesno("Formulário em andamento","Descartar os campos preenchidos para abrir outro arquivo?",parent=self):return
        chosen=filedialog.askopenfilename(parent=self,title="Selecione o index.html atualizado",filetypes=[("Página do acervo","*.html")])
        if chosen:
            if self.load_file(Path(chosen)): self.clear_form(force=True)

    def load_file(self,path):
        try: _,data,fingerprint=ler(path)
        except (OSError,ValueError,KeyError) as e:
            if self.testing:raise
            messagebox.showerror("Não foi possível abrir",str(e),parent=self);return False
        self.path=path.resolve();self.data=data;self.fingerprint=fingerprint
        self.path_label.configure(text=str(self.path))
        self.save_button.configure(state="normal")
        self.tree.delete(*self.tree.get_children())
        for r in sorted(data["sermons"],key=lambda r:r["date"],reverse=True):self.tree.insert("","end",iid=r["id"],values=(date.fromisoformat(r["date"]).strftime("%d/%m/%Y"),r["title"],r["preacher"]))
        for key in ("series","preacher"):self.inputs[key]["values"]=sorted({r[key] for r in data["sermons"] if r.get(key)},key=str.casefold)
        self.status.set(f'{len(data["sermons"])} sermões carregados. Os registros existentes são somente para consulta.')
        if not self.testing:
            try:self.settings.write_text(json.dumps({"index":str(self.path)},ensure_ascii=False),encoding="utf-8")
            except OSError:pass
        return True

    def update_calendar(self,*_):
        try:
            year=int(self.year.get())
            if not 2026<=year<=4099:raise ValueError()
        except ValueError:
            self.status.set("Escolha um ano de 2026 a 4099 e pressione Enter.")
            return
        if year==self.loaded_year:return
        self.loaded_year=year
        self.calendar_rows=domingos(year)
        self.sunday["values"]=[date.fromisoformat(r["date"]).strftime("%d/%m/%Y")+" — "+r["celebration"] for r in self.calendar_rows]
        self.sunday.set("")
        self.cal_tree.delete(*self.cal_tree.get_children())
        for r in self.calendar_rows:self.cal_tree.insert("","end",values=(date.fromisoformat(r["date"]).strftime("%d/%m/%Y"),r["celebration"],r["season"]))
        self.update_preview()

    def update_preview(self,*_):
        if not hasattr(self,"preview"):return
        index=self.sunday.current()
        row=self.calendar_rows[index] if index>=0 else None
        self.season_label.configure(text=(f'Estação: {row["season"]}  ·  Ciclo litúrgico: {row["liturgicalYear"]}' if row else "A estação e a celebração serão preenchidas ao escolher o domingo."))
        values={k:v.get().strip() for k,v in self.values.items()}
        self.preview.configure(text=f'{values["title"] or "Prévia do novo sermão"}\n{values["preacher"] or "Preletor"}  ·  {values["series"] or "Série"}\n'+(self.sunday.get() if row else "Selecione um domingo para continuar."))
        if not self._resetting:self.dirty=any(values.values()) or row is not None

    def clear_form(self,force=False):
        if self.dirty and not force and not messagebox.askyesno("Limpar formulário","Descartar os dados ainda não salvos?",parent=self):return
        self._resetting=True
        for v in self.values.values():v.set("")
        self.sunday.set("");self.update_preview()
        self._resetting=False;self.dirty=False

    def build_record(self):
        self.update_calendar()
        if self.sunday.current()<0 or self.year.get()!=str(self.loaded_year):raise ValueError("Escolha um ano válido e selecione um domingo da lista.")
        row=self.calendar_rows[self.sunday.current()]
        r={**row,**{k:v.get().strip() for k,v in self.values.items()},"id":uuid.uuid4().hex[:16],"publishedAt":datetime.now(timezone.utc).isoformat(),"legacy":False}
        validar_novo(r)
        r["originalText"]=f'Série "{r["series"]}" - {r["title"]} - {r["preacher"]}'
        return r

    def save(self):
        if not self.path:return
        try:
            r=self.build_record()
            conflicts=[s for s in self.data["sermons"] if s["url"]==r["url"] or s["date"]==r["date"]]
            if conflicts and not messagebox.askyesno("Confira antes de salvar","Já existe um sermão com a mesma data ou o mesmo link.\n\nAdicionar como OUTRO sermão, preservando o anterior?",parent=self):return
            if date.fromisoformat(r["date"])>date.today() and not messagebox.askyesno("Data futura","Este domingo ainda não aconteceu. Deseja cadastrar o sermão com essa data?",parent=self):return
            backup=adicionar(self.path,r,self.fingerprint)
            self.load_file(self.path);self.clear_form(force=True)
            self.status.set(f'Sermão salvo. Backup: {backup.name}. Publique o index.html pelo GitHub quando desejar.')
            messagebox.showinfo("Sermão salvo","O index.html foi atualizado e o acervo anterior foi preservado.\n\nUma cópia de segurança foi salva em:\n"+str(backup)+"\n\nA alteração ainda é local; publique pelo GitHub.",parent=self)
        except (OSError,ValueError,KeyError) as e:messagebox.showerror("Não foi possível salvar",str(e),parent=self)

    def show_record(self,*_):
        selected=self.tree.selection()
        if not selected:return
        r=next(r for r in self.data["sermons"] if r["id"]==selected[0])
        text=f'{r["originalText"]}\n\nData: {r["date"]}    Estação: {r["season"]}\n{r["celebration"]}\n\nLink original: {r["url"]}\n\nRegistro preservado. Nenhuma alteração é feita nesta aba.'
        self.record_text.configure(state="normal");self.record_text.delete("1.0","end");self.record_text.insert("1.0",text);self.record_text.configure(state="disabled")

    def close_app(self):
        if self.dirty and not messagebox.askyesno("Sair","Há um sermão não salvo. Sair e descartar o formulário?",parent=self):return
        self.destroy()


def self_test(path,report):
    original=Path(path).read_bytes()
    with tempfile.TemporaryDirectory() as temp:
        sample=Path(temp)/'index.html';sample.write_bytes(original)
        app=Integrador(sample,testing=True)
        app.update_idletasks()
        before=list(app.data['sermons'])
        assert len(app.tree.get_children())==len(before)
        app.year.set("2030");app.update_calendar()
        assert len(app.calendar_rows)==52 and all(date.fromisoformat(r["date"]).weekday()==6 for r in app.calendar_rows)
        app.sunday.current(0)
        for k,v in {"title":"Teste de interface","series":"Série de teste","preacher":"Preletor de teste","url":"https://drive.google.com/file/d/teste-interface/view?usp=sharing"}.items():app.values[k].set(v)
        record=app.build_record()
        assert record["date"]=="2030-01-06"
        app.geometry('850x690');app.update_idletasks()
        button_bottom=app.save_button.winfo_rooty()+app.save_button.winfo_height()
        assert button_bottom <= app.winfo_rooty()+app.winfo_height(), 'Botão salvar fora da janela mínima'
        # Exercita o mesmo comando do botão em uma cópia descartável do acervo.
        messagebox.askyesno=lambda *a,**k:True
        messagebox.showinfo=lambda *a,**k:None
        messagebox.showerror=lambda *a,**k:(_ for _ in ()).throw(AssertionError(str(a)))
        app.save()
        _,after,_=ler(sample)
        assert after['sermons'][:-1]==before
        assert after['sermons'][-1]['date']=='2030-01-06'
        assert len(list((Path(temp)/'backups').glob('*.html')))==1
        assert not app.dirty and not app.values['title'].get()
        result={"ok":True,"records":len(before),"sundays2030":len(app.calendar_rows),"minimumSize":[app.winfo_width(),app.winfo_height()],"savedInTemporaryCopy":True,"backupVerified":True}
        app.destroy()
    assert Path(path).read_bytes()==original
    Path(report).write_text(json.dumps(result,ensure_ascii=False),encoding="utf-8")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--file");parser.add_argument("--self-test",metavar="REPORT")
    args=parser.parse_args()
    if args.self_test:self_test(args.file,args.self_test)
    else:Integrador(args.file).mainloop()
