#include "cdda/trade_dialog.h"
#include <stdexcept>
#include <iostream>
#define CHECK(x) do{if(!(x))throw std::runtime_error(#x);}while(false)
int main(){
    cdda_client::TradeDialog v;v.id=4;v.quote=5;v.connection=9;v.name="Trader ] injection";v.can_confirm=true;
    cdda_client::TradeRow r;r.item.id=1;r.item.type="9mm";r.item.name="<color_c_red>Ammo</color>";r.item.category="ammo";r.item.charges=r.available=30;r.selected=3;r.trader=false;r.price=123;r.source="Backpack";v.rows.push_back(r);v.selected=1;v.quantity=3;
    auto icon=[](const std::string&){return std::string("cdda_items:fallback_generic");};
    auto form=v.form(icon);CHECK(form.find("Trader \\] injection")!=std::string::npos);CHECK(form.find("3/30")!=std::string::npos);CHECK(form.find("<color_c_red>")==std::string::npos);
    CHECK(form.find("cwm_inventory[5;1;1]")!=std::string::npos);CHECK(form.find("Review and confirm")!=std::string::npos);
    CHECK(form.find("quantity;;3")!=std::string::npos);CHECK(form.find("trade_own")!=std::string::npos);CHECK(form.find("trade_npc")!=std::string::npos);
    v.waiting=true;form=v.form(icon);CHECK(form.find("Waiting for the native trade result")!=std::string::npos);CHECK(form.find("accept;")==std::string::npos);
    CHECK(cdda_client::TradeDialog::money(-125)=="$-1.25");CHECK(v.row(0)==nullptr);CHECK(v.row(2)==nullptr);
    std::cout<<"Trade panels, escaping, quantities, native totals and pending-confirmation display PASS\n";
}
