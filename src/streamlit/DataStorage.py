import pandas as pd

import streamlit as st
from src.microspotreader import SpotList


class DataStorage:
    id: int = 0
    saved_data: dict = {}
    dataframe_display: pd.DataFrame = pd.DataFrame(
        columns=["Type", "Name", "Select", "id"]
    )
    edited_display: pd.DataFrame = pd.DataFrame(
        columns=["Type", "Name", "Select", "id"]
    )
    types = ["Image Data", "Prepared Data"]

    data_change: bool = False

    def update_id(self):
        self.id += 1

    def update_dataframe_display(self):
        for key, value in self.saved_data.items():
            if key not in self.dataframe_display["id"]:
                new_item = pd.Series(
                    {
                        "Type": value["type"],
                        "Name": value["name"],
                        "Select": False,
                        "id": key,
                    }
                )
                self.dataframe_display = pd.concat(
                    [self.dataframe_display, new_item.to_frame().T], ignore_index=True
                )

    def add_data(self, data, name: str, data_type: str):
        self.update_id()
        self.saved_data[self.id] = {"name": name, "type": data_type, "data": data}
        self.update_dataframe_display()

    def display_data(self):
        st.caption("Data Stored in Session:")
        # Warning if changes to stored data were not applied yet.
        if self.data_change:
            st.warning("Changes have not been applied yet!")

        self.edited_display = st.data_editor(
            self.dataframe_display,
            column_config={
                "Select": st.column_config.CheckboxColumn("Select", default=False),
                "id": None,
            },
            disabled=["Type"],
            use_container_width=True,
            hide_index=True,
            on_change=self.display_warning,
        )
        # Buttons for deleting data and applying changes to data.
        col1, col2 = st.columns(2)
        with col2:
            st.button(
                "Delete Selection", on_click=self.delete_data, use_container_width=True
            )

        with col1:
            st.button(
                "Apply Changes",
                on_click=self.apply_changes,
                use_container_width=True,
                type="primary",
            )

    def delete_data(self):
        self.apply_changes()

        self.dataframe_display = self.dataframe_display[
            self.dataframe_display["Select"] == False
        ]

        self.saved_data = {
            key: value
            for key, value in self.saved_data.items()
            if key in self.dataframe_display["id"]
        }

    def apply_changes(self):
        self.dataframe_display = self.edited_display
        self.data_change = False

    def display_warning(self):
        self.data_change = True

    def get_selected_names(self, data_type: str):
        return self.dataframe_display[
            self.dataframe_display["Select"]
            & (self.dataframe_display["Type"] == data_type)
        ]["Name"]

    def get_selected_data(self, data_type: str):
        return [
            value["data"]
            for key, value in self.saved_data.items()
            if key
            in self.dataframe_display[
                self.dataframe_display["Select"]
                & (self.dataframe_display["Type"] == data_type)
            ]["id"].to_list()
        ]

    def add_data_interface(self, data, data_type: str):
        with st.form("Add to Session", border=False):
            c1, c2 = st.columns(2)

            # Name of data, is customizable by user
            with c2:
                data_name = st.text_input(
                    "Name your Data",
                    placeholder="Name your Data",
                    label_visibility="collapsed",
                )

            # Adds the data to the current session, storage is explained in the documentation of the add_imgdata function.
            with c1:
                add = st.form_submit_button(
                    "Add current Data to Session",
                    type="primary",
                    use_container_width=True,
                )

            if add:
                if len(data_name) > 0:
                    self.add_data(data, data_name, data_type)
                else:
                    # Warning message if no name has been entered.
                    st.warning("Please enter a Name!")
